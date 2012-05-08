from datetime import datetime

from openspending.model import meta as db, Dataset
from openspending.model.common import TableHandler, JSONType


class Cuboid(TableHandler, db.Model):
    """ A cuboid is a partial pre-aggregation of a Dataset in which
    all facts have been grouped by one or multiple dimensions. """
    __tablename__ = 'cuboid'

    STATE_STALE = u'stale'
    STATE_ACTIVE = u'active'

    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.Unicode(), default=STATE_STALE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    dimensions = db.Column(JSONType, default=list)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))

    dataset = db.relationship(Dataset, backref=db.backref('cuboids',
                          lazy='dynamic'))

    def __init__(self, dataset, dimensions):
        self.dataset = dataset
        self.state = Cuboid.STATE_STALE
        self.dimensions = dimensions
        #self._load_data()

    @db.reconstructor
    def init(self):
        """ Create a SQLAlchemy model for the current cuboid, without
        creating the necessary table. This needs to be called both for
        access to the data and in order to generate the model
        physically. """
        self.bind = db.engine
        self.meta = self.dataset.meta

        self._init_table(self.meta, self.dataset.name,
                         'cuboid__' + str(self.id), id_type=None)
        count_ = db.Column('entries', db.Integer)
        self.table.append_column(count_)
        for dimension in self.dimensions:
            self.dataset[dimension].init(self.meta, self.table)
        for measure in self.dataset.measures:
            measure.init(self.meta, self.table)

        self.alias = self.table.alias('cuboid__' + str(self.id))

    def match(self, dimensions):
        if self.state != self.STATE_ACTIVE:
            return False
        for dimension in dimensions:
            if not dimension in self.dimensions:
                return False
        return True

    def generate(self):
        self.init()
        if db.engine.has_table(self.table.name):
            self.table.drop()

        self._generate_table()
        entries = db.func.count(self.dataset.alias.c.id).label("entries")
        fields = [entries]
        for measure in self.dataset.measures:
            a = db.func.sum(self.dataset.alias.c[measure.name])\
                .label(measure.name)
            fields.append(a)

        group_by = []
        for dimension_name in self.dimensions:
            dimension = self.dataset[dimension_name]
            fields.append(dimension.column_alias)
            group_by.append(dimension.column_alias)
        query = db.select(fields, group_by=group_by,
                          having=entries > 0)
        rp = self.dataset.bind.execute(query)
        while True:
            row = rp.fetchone()
            if row is None:
                break
            q = self.table.insert(dict(row.items()))
            self.dataset.bind.execute(q)
        self.state = self.STATE_ACTIVE
        db.session.add(self)
        db.session.flush()

    def __len__(self):
        rp = self.bind.execute(self.alias.count())
        return rp.fetchone()[0]
