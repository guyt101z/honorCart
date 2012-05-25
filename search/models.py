from database import Item

def search(query):
    return Item.query.all()
