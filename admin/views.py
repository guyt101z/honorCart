from admin import admin_bp
from flask import render_template, request, redirect, url_for, flash, jsonify
from flaskext.login import login_required, current_user
from models import get_users, get_config, update_max_tab, validate_max_tab, delete_user
from models import split_form_data, update_users


@admin_bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_page():
    if not current_user.isAdmin():
        flash(u'<strong>Error!</strong> You don\'t have permission to go there!', 'error')
        return redirect(url_for('main'))

    if request.method == 'POST':
        if request.args.get('source') == 'users':
            data = split_form_data(request.form)
            update_users(data)


    return render_template('admin.html', users=get_users(), config=get_config())


@admin_bp.route('/admin/updateConfig', methods=['POST'])
@login_required
def update_config():
    if not current_user.isAdmin():
        flash(u'<strong>Error!</strong> You don\'t have permission to go there!', 'error')
        return redirect(url_for('main'))

    errors = validate_max_tab(request.form.get('max_tab'))
    if errors == {}:
        update_max_tab(request.form.get('max_tab'))
        return jsonify(status='success')
    else:
        return jsonify(status='failure', errors=errors)


@admin_bp.route('/admin/delete/<int:userid>')
@login_required
def delete_user_page(userid):
    if not current_user.isAdmin():
        flash(u'<strong>Error!</strong> You don\'t have permission to go there!', 'error')
        return redirect(url_for('main'))

    delete_user(userid)
    return redirect(url_for('.admin_page') + '#users')
