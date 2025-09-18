#!/usr/bin/env python3
"""Blueprints for the api"""

from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix="/")
