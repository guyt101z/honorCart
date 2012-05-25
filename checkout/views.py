from checkout import checkout_bp
from flask import g, render_template, request, redirect, url_for, flash, session
from flaskext.login import login_required, current_user
from flask import json
from models import get_item, get_price, get_total, checkout_cart, take_money


@checkout_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    shopping_cart = json.loads(request.form.get('cartJson'))
    for cart_item in shopping_cart:
        item = get_item(cart_item.get('id'))
        cart_item['item'] = item
        cart_item['subtotal'] = get_price(item.price, cart_item.get('qty_desired'), item.pricebreaks)
    return render_template('checkout.html', cart_items=shopping_cart, total=get_total(shopping_cart))


@checkout_bp.route('/checkout/do', methods=['POST'])
@login_required
def checkout_do():
    print request.form
    shopping_cart = json.loads(request.form.get('cartJson'))
    if take_money(current_user.id, request.form.get('total')):
        for cart_item in shopping_cart:
            checkout_cart(shopping_cart)
            # Need to handle errors here
    return render_template('checkout_complete.html')
