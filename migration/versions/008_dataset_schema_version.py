from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    dataset = Table('dataset', meta, autoload=True)

    v = Column('schema_version', Unicode())
    v.create(dataset) 

