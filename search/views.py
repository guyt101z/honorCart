from search import search_bp
from flask import g, render_template, request, redirect, url_for, flash, session
from flaskext.login import login_required
from models import search


@search_bp.route('/searchItem')
@login_required
def search_results():
    items = search(request.args.get('q'))
    return render_template('item_shelf.html', items=items)
