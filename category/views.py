from category import category_bp
from flask import render_template, request, redirect, url_for, flash, jsonify
from flaskext.login import login_required, current_user
from models import get_items, get_item


@category_bp.route('/category/<int:catid>')
@login_required
def display_shelf(catid):

    return render_template('item_shelf.html', items=get_items(catid))


@category_bp.route('/category/getItemInfo')
@login_required
def get_item_info_modal_content():
    item_id = request.args.get('item_id')
    return render_template('item_info_modal_content.html', item=get_item(item_id))


@category_bp.route('/category/alertShopkeep', methods=['POST'])
@login_required
def alert_shopkeep():
    flash('Thanks for alerting the shop keeper!', 'success')
    return redirect(request.referrer)
