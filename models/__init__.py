#!/usr/bin/env python3
"""Initialize storage and models"""

from models.engine import Storage
from models.user import User
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from models.category import Category
from models.carousel_image import CarouselImage


storage = Storage()
storage.reload()
