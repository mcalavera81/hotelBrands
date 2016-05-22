import jsonpickle,logging, settings


def mongodb_persist(*,organizations=[], brands=[]):
    try:
        db = settings.client[settings.db_name]
        db[settings.collections['organization']].delete_many({})
        db[settings.collections['organization']].insert_many(org.to_dict() for org in organizations)

        db[settings.collections['brand']].delete_many({})
        db[settings.collections['brand']].insert_many(brand.to_dict() for brand in brands)

    except Exception as exc:
        logging.warning("Mongodb-related Exception:%s" % exc)


def find_entities(*, entity_type, status=None):
    try:
        db = settings.client[settings.db_name]
        query = {"status": status} if status else {}
        found_docs = db[settings.collections[entity_type]].find(query)
        return found_docs
    except Exception as exc:
        logging.warning("Mongodb-related Exception:%s" % exc)


def store_entities(*,entities):
    try:
        db = settings.client[settings.db_name]
        for entity in entities:
            db[settings.collections[entity.entity_type]].replace_one({"entity_id":entity.entity_id},entity.to_dict())
    except Exception as exc:
        logging.warning("Mongodb-related Exception:%s" % exc)