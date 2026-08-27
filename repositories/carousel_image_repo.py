#!/usr/bin/env python3
"""Repository for CarouselImage - db access mirrors UserRepo"""
from models import storage
from models.carousel_image import CarouselImage


class CarouselImageRepo:
    """Data access layer for carousel images"""

    @staticmethod
    def all():
        """Return every carousel image, ordered by position then creation time"""
        images = list(storage.all(CarouselImage))
        images.sort(key=lambda i: (getattr(i, 'position', 0) or 0, i.created_at))
        return images

    @staticmethod
    def get(image_id):
        """Return a single carousel image by id, or None"""
        return storage.get(CarouselImage, image_id)

    @staticmethod
    def new(**kwargs):
        """Create and persist a new carousel image record"""
        if not kwargs.get('image_url') or not kwargs.get('filename'):
            raise ValueError("image_url and filename are required")
        image = CarouselImage(**kwargs)
        image.save()
        return image

    @staticmethod
    def delete(image_id):
        """Delete a carousel image record. Returns the deleted object or None."""
        image = storage.get(CarouselImage, image_id)
        if not image:
            return None
        storage.delete(image)
        storage.save()
        return image
