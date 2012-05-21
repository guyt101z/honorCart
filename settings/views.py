from settings import settings_bp
from flask import render_template, request, redirect, url_for, flash
from flaskext.login import login_required, current_user
from models import update_non_oid_user, update_oid_user


@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def admin_page():
    if request.method == 'POST':
        if current_user.openid == None:
            if request.form.get('password1') == request.form.get('password2'):
                password = None
                if request.form.get('password1') != '':
                    password = request.form.get('password1')
                update_non_oid_user(current_user, request.form.get('email'),
                    password)
                flash(u'<strong>Success!</strong> Settings Successfully Saved!',
                    'success')
            else:
                flash(u'<strong>Error!</strong> Passwords must match!',
                    'error')
        else:
            update_oid_user(current_user, request.form.get('name'),
                request.form.get('email'))
            flash(u'<strong>Success!</strong> Settings Successfully Saved!',
                    'success')
    return render_template('settings.html')
