from checkout import checkout_bp
from flask import g, render_template, request, redirect, url_for, flash, session
from flaskext.login import login_required
from flask import json


@checkout_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    print request.form
    print json.loads(request.form.get('cartJson'))
    return render_template('checkout.html')
