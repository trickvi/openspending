

from sqlalchemy import Integer, UnicodeText, Float, Unicode
from nose.tools import assert_raises

from openspending.test.helpers import load_fixture
from openspending.test import DatabaseTestCase, helpers as h

from openspending.model import meta as db
from openspending.model import Dataset, Cuboid


class TestCuboid(DatabaseTestCase):

    def setup(self):
        super(TestCuboid, self).setup()
        self.ds = load_fixture('cra')

    def test_generate_basic(self):
        cb1 = Cuboid(self.ds, ['from', 'region'])
        db.session.add(cb1)
        db.session.flush()
        cb1.generate()
        assert len(cb1) == 10, len(cb1)
        cb2 = Cuboid(self.ds, ['from'])
        db.session.add(cb2)
        db.session.flush()
        cb2.generate()
        assert len(cb2) == 7, len(cb2)

        assert len(cb1.table.columns) == 5, len(cb1.table.columns)
        assert 'entries' in cb1.table.columns
        #assert False

    def test_match(self):
        cb1 = Cuboid(self.ds, ['from', 'region'])
        db.session.add(cb1)
        db.session.flush()
        assert cb1.match(['from'])
        assert cb1.match(['from', 'region'])
        assert not cb1.match(['to'])
