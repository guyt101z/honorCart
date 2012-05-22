from database import Item
import flask.ext.whooshalchemy

def search(query):
    return Item.query.whoosh_search(query).all()
