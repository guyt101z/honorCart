from flask import Blueprint

search_bp = Blueprint('search', __name__)

import models
import views
