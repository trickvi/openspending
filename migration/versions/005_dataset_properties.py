from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    dataset = Table('dataset', meta, autoload=True)

    entry_custom_html = Column('entry_custom_html', Unicode())
    entry_custom_html.create(dataset) 
