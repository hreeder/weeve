from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
invTypes = Table('invTypes', pre_meta,
    Column('typeID', INTEGER(display_width=11), primary_key=True, nullable=False),
    Column('groupID', INTEGER(display_width=11)),
    Column('typeName', VARCHAR(length=200)),
    Column('description', VARCHAR(length=6000)),
    Column('mass', DOUBLE(asdecimal=True)),
    Column('volume', DOUBLE(asdecimal=True)),
    Column('capacity', DOUBLE(asdecimal=True)),
    Column('portionSize', INTEGER(display_width=11)),
    Column('raceID', TINYINT(display_width=3, unsigned=True)),
    Column('basePrice', DECIMAL(precision=19, scale=4)),
    Column('published', TINYINT(display_width=1)),
    Column('marketGroupID', INTEGER(display_width=11)),
    Column('chanceOfDuplicating', DOUBLE(asdecimal=True)),
)

alliance = Table('alliance', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=120)),
)

character = Table('character', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('key_id', Integer),
    Column('name', String(length=120)),
    Column('corpid', Integer),
    Column('balance', Integer),
    Column('sp', Integer),
    Column('clonesp', Integer),
)

corp = Table('corp', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=120)),
    Column('allianceid', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['invTypes'].drop()
    post_meta.tables['alliance'].create()
    post_meta.tables['character'].create()
    post_meta.tables['corp'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['invTypes'].create()
    post_meta.tables['alliance'].drop()
    post_meta.tables['character'].drop()
    post_meta.tables['corp'].drop()
