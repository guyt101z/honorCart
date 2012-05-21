from flask import Flask, render_template, g
from database import Category
import login
import admin
import settings
import items
import category


app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.register_blueprint(login.login_bp)
login.models.init_oid(app)
login.models.init_login(app)

app.register_blueprint(admin.admin_bp)
app.register_blueprint(settings.settings_bp)
app.register_blueprint(items.items_bp)
app.register_blueprint(category.category_bp)


@app.before_request
def update_categories():
    g.categories = Category.query.all()


@app.route("/")
def main():
    return render_template("base.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/rules")
def daRules():
    print app.url_map
    return "Printed"


if __name__ == "__main__":
    app.run(debug=True)
