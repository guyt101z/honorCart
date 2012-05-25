from database import db, Item, User, Config


def get_item(item_id):
    return Item.query.filter_by(id=item_id).first()


def get_config():
    return Config.query.first()


def get_price(price, qty, pricebreaks):
    pct_off = 0
    for pb in pricebreaks:
        if qty >= pb.qty:
            pct_off = pb.percent
    return price * ((100 - pct_off) / 100) * qty


def get_total(shopping_cart):
    total = 0
    for cart_item in shopping_cart:
        total += cart_item.get('subtotal')
    return total


def checkout_cart(shopping_cart):
    all_okay = True
    for cart_item in shopping_cart:
        item = Item.query.filter_by(id=cart_item.get('id')).first()
        qty = cart_item.get('qty_desired')
        if item.inStock >= qty:
            item.inStock -= qty
        else:
            all_okay = False
        db.session.commit()

    return all_okay


def take_money(id, total):
    user = User.query.filter_by(id=id).first()
    if user.balance - float(total) < get_config().max_tab:
        return False
    else:
        user.balance -= float(total)
        db.session.commit()
        return True
