from flask import Flask, render_template, g, request, jsonify
from database import db, Item, Category, init_db_app
import login
import admin
import settings
import items
import category
import search
import checkout
import add_money
from config import global_config
from global_mail import init_mail

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

global_config(app)

init_db_app(app)
init_mail(app)

app.register_blueprint(login.login_bp)
login.models.init_oid(app)
login.models.init_login(app)

app.register_blueprint(admin.admin_bp)
app.register_blueprint(settings.settings_bp)
app.register_blueprint(items.items_bp)
app.register_blueprint(category.category_bp)
app.register_blueprint(search.search_bp)
app.register_blueprint(checkout.checkout_bp)
app.register_blueprint(add_money.add_money_bp)


# dirty hack to get around issues in whoosh
@app.before_first_request
def test():
    item = Item.query.first()
    item.inStock -= 1
    db.session.add(item)
    db.session.commit()
    item.inStock += 1
    db.session.add(item)
    db.session.commit()
    print "Test!"


@app.before_request
def update_categories():
    cats = Category.query.all()
    db.session.expunge_all()
    g.categories = cats


@app.route("/")
def main():
    return render_template("base.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/newbie")
def newbie():
    return render_template("newbie.html")


@app.route("/money")
def money():
    return render_template("money.html")


@app.route("/rules")
def daRules():
    print app.url_map
    return "Printed"


@app.route("/getCartDivContents", methods=['POST'])
def theCart():
    cart_items = []
    cart_items.extend(request.json)

    print cart_items

    does_not_exist = {}
    qty_return = {}

    for cart_item in cart_items:
        item = get_item(cart_item.get('id'))
        if item:  # Item exists
            cart_item['item'] = item
            if item.inStock < cart_item.get('qty_desired'):
                if not cart_item.get('id') in qty_return:
                    qty_return[cart_item.get('id')] = {}
                cart_item['qty_desired'] = item.inStock  # Force qty display to not increment
                qty_return[cart_item.get('id')] = item.inStock
            cart_item['subtotal'] = checkout.models.get_price(item.price, cart_item.get('qty_desired'), item.pricebreaks)
        else:  # Item does not exist
            print "No Exist"
            if not cart_item.get('id') in does_not_exist:
                does_not_exist[cart_item.get('id')] = {}
            does_not_exist[cart_item.get('id')] = True
            cart_items.remove(cart_item)  # Remove item so it does not render.
    return jsonify({'html': render_template('cart_div_content.html', cart_items=cart_items), 'qty_return': qty_return, 'does_not_exist': does_not_exist})


def get_item(item_id):
    return Item.query.filter_by(id=item_id).first()



if __name__ == "__main__":
    app.run(debug=True)
