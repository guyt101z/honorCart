from login import login_bp
from flask import g
from flaskext.openid import OpenID
from flaskext.login import LoginManager
from database import db, User

oid = OpenID(fs_store_path='')
login_manager = LoginManager()

login_manager.login_view = "login.do_login"


def getAnonUser():
    return User("Anonymous", "None")

login_manager.anonymous_user = getAnonUser


@login_bp.before_request
def lookup_user():
    """ Toss the user in the g object if it's in the database """
    g.user = None
#    if 'openid' in session:
#        g.user = User.query.filter_by(openid=session['openid']).first()


def user_exists(username):
    user = User.query.filter_by(name=username).all()
    if(len(user) == 1 and user.openid == None):
        return True
    else:
        return False


def validate_password(username, password):
    user = User.query.filter_by(name=username).first()
    return user.checkPassword(password)


def init_oid(app):
    return oid.init_app(app)


def init_login(app):
    return login_manager.setup_app(app)


@login_manager.user_loader
def get_user_dec(openidnum):
    return User.query.filter_by(openid=openidnum).first()


def get_user(openidnum):
    return User.query.filter_by(openid=openidnum).first()


def get_user_non_oid(username):
    return User.query.filter_by(name=username).first()


def add_user(name, email, openidnum):
    newUser = User(name, email, openidnum, superjesus=True)
    db.session.add(newUser)
    db.session.commit()
    return newUser
