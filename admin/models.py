from database import db, User, Config


def get_users():
    users = User.query.all()
    return users


def get_config():
    return Config.query.first()


def update_max_tab(max_tab):
    config = get_config()
    config.max_tab = max_tab
    db.session.add(config)
    db.session.commit()


def validate_max_tab(max_tab):
    error = {}
    try:
        if float(max_tab) > 0:
            error['warning'] = "<strong>Warning! </strong>This effectively enforces a minimum balance."
    except ValueError:
        error['error'] = "<strong>Error! </strong>Enter a valid number."

    return error


def delete_user(userid):
    bad_user = User.query.filter_by(id=userid).first()
    db.session.delete(bad_user)
    db.session.commit()


def update_users(user_dict):
    for userid, values in user_dict.iteritems():
        user = User.query.filter_by(id=userid).first()
        user.username = values['name']
        user.email = values['email']
        user.balance = values['balance']
        if values['password'] is not u'' and user.openid is None:
            user.setPassword(values['password'])
        if values.get('isAdmin') == 'on':
            user.admin = True
        db.session.add(user)
    db.session.commit()


def split_form_data(input):
    output = dict()
    for key, value in input.iteritems(multi=True):
        (id, outKey) = key.split('-', 1)
        if id not in output:
            output[id] = {}
        output[id][outKey] = value
    return output
