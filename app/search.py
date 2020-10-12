from flask import current_app
from elasticsearch import helpers


def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = str(getattr(model, field))
    for field in model.__searchableList__:
        payload[field] = [str(x) for x in getattr(model, field)]
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page - 1) * per_page, 'size': per_page})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']


def batch_index(index, model):
    if not current_app.elasticsearch:
        return
    actions = []
    i = 0
    for obj in model.query:
        i += 1
        payload = {}
        for field in obj.__searchable__:
            payload[field] = str(getattr(obj, field))
        for field in obj.__searchableList__:
            payload[field] = [str(x) for x in getattr(obj, field)]

        actions.append({
            "_index": index,
            "_id": obj.id,
            "_source": payload
        })
        print(i)
    helpers.bulk(current_app.elasticsearch, actions)
