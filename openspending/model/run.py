from datetime import datetime

from openspending.model import meta as db
from openspending.model.dataset import Dataset


class Run(db.Model):
    """ A run is a generic grouping object for background operations
    that perform logging to the frontend. """

    __tablename__ = 'run'

    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETE = 'complete'
    STATUS_FAILED = 'failed'

    id = db.Column(db.Integer, primary_key=True)
    operation = db.Column(db.Unicode(2000))
    status = db.Column(db.Unicode(2000))
    message = db.Column(db.Unicode(2000))
    time_start = db.Column(db.DateTime, default=datetime.utcnow)
    time_end = db.Column(db.DateTime)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'),
                           nullable=True)

    dataset = db.relationship(Dataset,
                              backref=db.backref('runs', lazy='dynamic'))

    def __init__(self, operation, status, dataset, message=None):
        self.operation = operation
        self.status = status
        self.dataset = dataset
        self.message = message

    @classmethod
    def by_id(cls, id):
        return db.session.query(cls).filter_by(id=id).first()


