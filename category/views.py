from category import category_bp
from flask import render_template, request, redirect, url_for, flash, jsonify
from flaskext.login import login_required, current_user
from models import get_items


@category_bp.route('/category/<int:catid>')
@login_required
def display_shelf(catid):

    return render_template('item_shelf.html', items=get_items(catid))