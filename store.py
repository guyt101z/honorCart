from flask import Flask, render_template
import login
import admin
import settings
from flaskext.login import current_user


app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.register_blueprint(login.login_bp)
login.models.init_oid(app)
login.models.init_login(app)

app.register_blueprint(admin.admin_bp)

app.register_blueprint(settings.settings_bp)


@app.route("/")
def main():
    return render_template("base.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/addItem")
def addItemTest():
    return render_template("addItem.html")


@app.route("/rules")
def daRules():
    print app.url_map
    return "Printed"


if __name__ == "__main__":
    app.run(debug=True)
