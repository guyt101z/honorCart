from database import db, Item, Category


def get_items(category):
    return Item.query.filter_by(category_id=category).all()


def get_item(itemid):
    return Item.query.filter_by(id=itemid).first()
