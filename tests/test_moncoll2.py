import json
from pathlib import Path
from pymongo import UpdateOne
import pytest
from moncoll2 import MC, BulkItemNotIdError, to_bulklist


@pytest.fixture()
def settings():
    settings_path = Path.home() / '.config/mongos/test_settings.json'
    if settings_path.exists():
        return json.loads(settings_path.read_text())
    else:
        return {
            "username": "testuser",
            "password": "testpass",
            "host": "localhost",
            "port": 12345,
            "coll_name": "test_collection",
            "db_name": "test_db"
        }


def test_hard_1(settings):
    with MC(settings) as coll:
        assert coll.full_name == 'test_db.test_collection'
        coll.insert_one({"a": 1})
        res = coll.find_one()
        assert res['a'] == 1
        coll.drop()


def test_hard_1_2(settings):
    with MC(settings) as coll:
        assert coll.full_name == 'test_db.test_collection'
        coll.insert_one({"a": 1})
        res = coll.find_one()
        assert res['a'] == 1
    with MC(settings) as coll:
        assert coll.full_name == 'test_db.test_collection'
        coll.insert_one({"b": 2})
        res = coll.find_one({'b': {'$exists': True}})
        assert res['b'] == 2
        coll.drop()


def test_hard_2(settings):
    li = to_bulklist([
        {"name": "Karin", "gender": "female"},
        {"name": "Decker", "gender": "male"}
    ], 'name')
    with MC(settings) as coll:
        res = coll.bulk_write(li)
        assert res.upserted_count == 2
        assert coll.find_one({"gender": "male"}) == {
            "_id": "Decker",
            "name": "Decker",
            "gender": "male"
        }
        coll.drop()


class TestToBulklist:
    def test_not_id(self):
        li = [
            {"name": "Karin", "gender": "female"},
            {"name": "Decker", "gender": "male"}
        ]
        assert to_bulklist(li, "name") == [
            UpdateOne(
                {"_id": "Karin"},
                {"$set": {"name": "Karin", "gender": "female", "_id": "Karin"}},
                True,
                None,
                None,
                None,
            ),
            UpdateOne(
                {"_id": "Decker"},
                {"$set": {"name": "Decker", "gender": "male", "_id": "Decker"}},
                True,
                None,
                None,
                None,
            ),
        ]

    def test_with_id(self):
        data = [
            {"_id": "5fc3af959f9e4b17a00d15f5", "name": "Mosley", "gender": "male"},
            {"_id": "5fc3af9584542f2b3fb85bdf", "name": "Kelly", "gender": "male"},
        ]
        assert to_bulklist(data) == [
            UpdateOne(
                {"_id": "5fc3af959f9e4b17a00d15f5"},
                {
                    "$set": {
                        "_id": "5fc3af959f9e4b17a00d15f5",
                        "name": "Mosley",
                        "gender": "male",
                    }
                },
                True,
                None,
                None,
                None,
            ),
            UpdateOne(
                {"_id": "5fc3af9584542f2b3fb85bdf"},
                {
                    "$set": {
                        "_id": "5fc3af9584542f2b3fb85bdf",
                        "name": "Kelly",
                        "gender": "male",
                    }
                },
                True,
                None,
                None,
                None,
            ),
        ]

    def test_bulk_item_not_id_error(self):
        li = [{"name": "Karin", "gender": "female"}, {"name": "Decker", "gender": "male"}]
        with pytest.raises(BulkItemNotIdError) as e:
            to_bulklist(li)
        assert "_id property does not exist: {'name': 'Karin', 'gender': 'female'}" in str(e)

    def test_bulk_invalid_type(self):
        with pytest.raises(TypeError) as e:
            to_bulklist({'a': 1})
        assert "must be a list" in str(e)
