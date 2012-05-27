from database import db, User


def validate_float(input):
    try:
        float(input)
        return True
    except ValueError:
        return False
