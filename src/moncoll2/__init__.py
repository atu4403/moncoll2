"""
.. include:: ../../README.md
"""
import copy
from pymongo import MongoClient, UpdateOne


class MC:
    """接続情報を元にcollectionを取り出す
    Args:
        settings (dict): pymongoのMongoClientに渡す引数にdb_nameとcollection_nameを加えたもの
    Examples:
        >>> settings = {'coll_name': 'test_coll', 'db_name': 'test_db'}
        >>> with MC(settings) as coll:
        ...     coll.full_name
        'test_db.test_coll'
    """

    def __init__(self, settings: dict):
        d = copy.deepcopy(settings)
        self.db_name = d.get('db_name') or 'test'
        self.collection_name = d.get('coll_name') or d.get('collection_name') or 'test_coll'
        d.pop('db_name', None)
        d.pop('coll_name', None)
        d.pop('collection_name', None)
        self.opts = d

    def __enter__(self):
        self.client = MongoClient(**self.opts)
        db = self.client[self.db_name]
        return db[self.collection_name]

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


class BulkItemNotIdError(Exception):
    """to_bulklistにて dict[idname]が存在しない場合に投げる例外"""

    pass


def to_bulklist(_list: list, idname: str = "_id") -> list:
    """listをbulk_writeで使用できる形式にする
    Args:
        _list (list): 元になるlist
        idname (str): _idになる項目名、元になるlistに含まれるなら省略可能
    Returns:
        list: bulk_writeで使用できる形式のlist
    Raises:
        BulkItemNotIdError: 元のlistに`_id`という項目が含まれておらず、かつ引数`idname`が指定されていない場合に発生
    Examples:
        >>> li = [
        ...     {"name": "Karin", "gender": "female"},
        ...     {"name": "Decker", "gender": "male"}
        ... ]
        >>> res = to_bulklist(li, 'name')
        >>> res[0]
        UpdateOne({'_id': 'Karin'}, {'$set': {'name': 'Karin', 'gender': 'female', '_id': 'Karin'}}, True, None, None, None)
    """
    if not type(_list) is list:
        raise TypeError("must be a list")

    def _fn(_dict: dict):
        if not _dict.get(idname):
            raise BulkItemNotIdError(f"{idname} property does not exist: {_dict}")
        _dict["_id"] = _dict[idname]
        return UpdateOne({"_id": _dict["_id"]}, {"$set": _dict}, upsert=True)

    return list(map(_fn, _list))
