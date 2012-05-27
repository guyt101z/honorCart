from flask import Blueprint

add_money_bp = Blueprint('add_money', __name__, template_folder='templates')

import models
import views
