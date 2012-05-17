from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash, \
     check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dataStore.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    openid = db.Column(db.String(4095))
    admin = db.Column(db.Boolean)
    verified = db.Column(db.Boolean)
    balance = db.Column(db.Float)
    password_hash = db.Column(db.String(80))

    def __init__(self, username, email, openid=None, admin=False, balance=0):
        self.username = username
        self.email = email
        self.openid = openid
        self.admin = admin
        self.balance = balance

    def __repr__(self):
        return '<User %r>' % self.username

    def is_active(self):
        """
        Returns `True`.
        """
        return True

    def is_authenticated(self):
        """
        Returns `True`.
        """
        if self.username == "Anonymous":
            return False
        else:
            return True

    def is_anonymous(self):
        """
        Returns `False`.
        """
        if self.username == "Anonymous":
            return True
        else:
            return False

    def isAdmin(self):
        """
        Get Admin Status
        """
        return self.admin

    def setPassword(self, password):
        self.password_hash = generate_password_hash(password)

    def checkPassword(self, password):
        return check_password_hash(self.pw_hash, password)

    def get_id(self):
        """
        Assuming that the user object has an `id` attribute, this will take
        that and convert it to `unicode`.
        """
        try:
            return unicode(self.openid)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override get_id")


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(16383))
    price = db.Column(db.Float)
    inStock = db.Column(db.Integer)
    picture = db.Column(db.String(1024))
    category = db.relationship('Category', backref="item", lazy='dynamic', uselist=False)

    pricebreaks = db.relationship('PriceBreak', backref="item", lazy='dynamic')

    def __init__(self, name, description, price, inStock, picture, category, warning=None):
        self.name = name
        self.description = description
        self.price = price
        self.inStock = inStock
        self.picture = picture
        self.category = category
        if(warning is not None):
            self.warning = warning

    def __repr__(self):
        return '<Item %r, %r>' % (self.name, self.category)

    def __str__(self):
        return '<Item %r, %r>' % (self.name, self.category)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name


class PriceBreak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Integer)
    percent = db.Column(db.Float)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))

    def __init__(self, qty, percent, item_id):
        self.qty = qty
        self.percent = percent
        self.item_id = item_id


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    admin = User("Admin", "admin@example.com", admin=True)
    admin.setPassword("admin")
    db.session.add(admin)
    db.session.commit()
