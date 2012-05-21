from database import db, User


def update_non_oid_user(updated_user, email, password=None):
    user = User.query.filter_by(id=updated_user.id).first()
    user.email = email
    if password != None:
        user.setPassword(password)
    db.session.add(user)
    db.session.commit()


def update_oid_user(updated_user, username, email):
    user = User.query.filter_by(id=updated_user.id).first()
    user.username = username
    user.email = email
    db.session.add(user)
    db.session.commit()
