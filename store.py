from flask import Flask, render_template
from login import login_bp


app = Flask(__name__)
app.register_blueprint(login_bp)
DEBUG = True


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
