#!/usr/bin/env python3
"""CarouselImage model"""
import models
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Integer


class CarouselImage(BaseModel, Base):
    """Manage CarouselImage"""
    __tablename__ = 'carousel_images'

    image_url = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    position = Column(Integer, default=0)
    uploaded_by = Column(String(60), nullable=True)
