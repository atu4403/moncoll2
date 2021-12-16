pymongoの単純なラッパー。接続情報、db_name、collection_nameをまとめてdictに含めることでDB操作のコードをシンプルにする。

[comment]: <> ([![Test]&#40;https://github.com/atu4403/moncoll2/actions/workflows/test.yml/badge.svg&#41;]&#40;https://github.com/atu4403/moncoll2/actions/workflows/test.yml&#41;)

[comment]: <> ([![PyPI version]&#40;https://badge.fury.io/py/moncoll2.svg&#41;]&#40;https://badge.fury.io/py/moncoll2&#41;)

[comment]: <> (document link)

[comment]: <> (## Install)

[comment]: <> (```bash)

[comment]: <> (pip install moncoll2)

[comment]: <> (```)

## Useit

### MC(settings: dict)-> pymongo.collection.Collection

settingsを元にしてcollectionを返す。with構文の中で操作をする事によってDBのcloseを確実に行う。

```py
from moncoll2 import MC

settings = {
    "username": "testuser",
    "password": "testpass",
    "host": "192.168.0.99",
    "port": 12345,
    "coll_name": "test_collenction",
    "db_name": "test_db"
}

with MC(settings) as coll:
    assert coll.full_name == 'test_db.test_collenction'
    coll.insert_one({"a": 1})
    res = coll.find_one()
    assert res['a'] == 1
    coll.drop()
```

#### Args

settings (dict): pymongoのMongoClientに渡す引数にdb_nameとcollection_nameを加えたもの

[mongo_client – Tools for connecting to MongoDB — PyMongo 4.0.1 documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html)

### to_bulklist(_list: list, idname: str = "_id") -> list:

listをbulk_writeで使用できる形式にする

#### Args

_list (list): 元になるlist idname (str): _idになる項目名、元になるlistに含まれるなら省略可能

#### Returns

list: bulk_writeで使用できる形式のlist

#### Raises

BulkItemNotIdError: 元のlistに`_id`という項目が含まれておらず、かつ引数`idname`が指定されていない場合に発生

#### Examples:

```python
>>> li = [
...     {"name": "Karin", "gender": "female"},
...     {"name": "Decker", "gender": "male"}
... ]
>>> res = to_bulklist(li, 'name')
>>> res[0]
UpdateOne({'_id': 'Karin'}, {'$set': {'name': 'Karin', 'gender': 'female', '_id': 'Karin'}}, True, None, None, None)
```
