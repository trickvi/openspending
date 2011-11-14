import logging
from datetime import datetime

from openspending.model import meta as db
from openspending.model.run import Run


class RunLogRecord(db.Model):
    __tablename__ = 'run_log_record'

    CATEGORY_SYSTEM = 'system'
    CATEGORY_MODEL = 'model'
    CATEGORY_DATA = 'data'

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('run.id'))
    
    category = db.Column(db.Unicode)
    level = db.Column(db.Unicode)
    message = db.Column(db.Unicode)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    error_type = db.Column(db.Unicode)
    error_file = db.Column(db.Unicode)
    error_module = db.Column(db.Unicode)
    error_line = db.Column(db.Unicode)
    error_function = db.Column(db.Unicode)

    source_file = db.Column(db.Unicode)
    source_row = db.Column(db.Integer)

    attribute = db.Column(db.Unicode)
    column = db.Column(db.Unicode)
    data_type = db.Column(db.Unicode)
    value = db.Column(db.Unicode)

    run = db.relationship(Run, backref=db.backref('records',
                          lazy='dynamic'))

    def __init__(self, run, category, level, message):
        self.run = run
        self.category = category
        self.level = level
        self.message = message

    @classmethod
    def by_id(cls, id):
        return db.session.query(cls).filter_by(id=id).first()


class RunLogger(logging.Logger):

    def __init__(self, run, level=logging.DEBUG):
        self.run = run
        if run.dataset:
            self.name = run.dataset.name
        self.level = level

    def handle(self, record):
        rec = RunLogRecord(self.run, 
                           RunLogRecord.CATEGORY_SYSTEM,
                           self.level,
                           record.getMessage())

        rec.error_type = record.name
        rec.error_file = record.filename
        rec.error_module = record.module
        rec.error_line = record.lineno
        rec.error_function = record.funcName

        #session = db.create_scoped_session()
        #session.begin()
        db.session.add(rec)
        db.session.flush()
        #session.commit()

