from flask import Blueprint

login_bp = Blueprint('login', __name__)

import models
import views
