from login import login_bp
from flaskext.login import login_user, current_user, logout_user, login_required
from models import oid, get_user, add_user, user_exists, validate_password, get_user_non_oid, login_manager
from flask import g, render_template, request, redirect, url_for, flash, session


@login_bp.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def do_login():
    if current_user.is_authenticated():
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        print request.form
        openid = request.form.get('openid')
        if openid:
            print openid
            return oid.try_login(openid, ask_for=['email', 'fullname',
                                                  'nickname'])
        elif request.form.get('login') == 'noOpenId':
            username = request.form.get('username')
            password = request.form.get('password')
            if(user_exists(username) and validate_password(username, password)):
                print "valid"
                user = get_user_non_oid(username)
                print user
                login_user(user)
        flash(u'Bad Username or Password', 'login_error')
        return redirect(url_for('main'))

    if request.method == 'GET':
        return redirect(oid.get_next_url())


@oid.after_login
def create_or_login(resp):
    user = get_user(resp.identity_url)
    session['openid'] = resp.identity_url
    if user is not None:
        flash(u'Successfully signed in')
        login_user(user)
        print 'logged in'
        return redirect(url_for('main'))
    return redirect(url_for('.create_profile', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))


@login_bp.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    if current_user.is_authenticated() or 'openid' not in session or \
    g.user is not None:
        return redirect(url_for('main'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if not name:
            flash(u'Error: you have to provide a name')
        elif '@' not in email:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            login_user(add_user(name, email, session['openid']))
            return redirect(oid.get_next_url())
    return render_template('create_profile.html', next_url=oid.get_next_url(),
    disable_login=True)


@login_bp.route('/logout')
@login_required
def do_logout():
    logout_user()
    return redirect(url_for('main'))


@login_manager.unauthorized_handler
def unauthorized():
    flash(u'You must log on to go there!', 'login_error')
    return redirect(url_for('main'))
