#!/usr/bin/env python3
"""Blueprints for the api"""

from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix="")

from api.v1.views.products import *
from api.v1.views.users import *
from api.v1.views.categories import *
from api.v1.views.orders import *
from api.v1.views.auth import *
