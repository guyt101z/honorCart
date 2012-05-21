from flask import Blueprint

items_bp = Blueprint('items', __name__, template_folder='templates')

import models
import views
