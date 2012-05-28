from database import db, User


def validate_float(input):
    try:
        float(input)
        return True
    except ValueError:
        return False


def add_to_user_balance(user_id, money):
    user = User.query.filter_by(id=user_id).first()
    user.balance += money
    db.session.commit()
