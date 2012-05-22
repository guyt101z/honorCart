from flask import Flask, render_template, g, request
from database import db, Item, Category, init_db_app
import login
import admin
import settings
import items
import category
import search
from global_mail import init_mail

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

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
    g.categories = Category.query.all()


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
    for dict in cart_items:
        dict['item'] = get_item(dict.get('id'))
    return render_template('cart_div_content.html', cart_items=cart_items)


def get_item(item_id):
    return Item.query.filter_by(id=item_id).first()


if __name__ == "__main__":
    app.run(debug=True)
