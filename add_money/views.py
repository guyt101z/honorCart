from add_money import add_money_bp
from flask import render_template, request, redirect, url_for, flash, jsonify
from flaskext.login import login_required, current_user


@add_money_bp.route('/addMoney')
@login_required
def add_money_view():
    return render_template('add_money.html')
