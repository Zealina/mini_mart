#!/usr/bin/env python3
"""Pending staff access invitations."""

from sqlalchemy import Column, String, UniqueConstraint
from models.base_model import Base, BaseModel


class PendingStaffAccess(BaseModel, Base):
    """Stores staff role access until the invited email creates an account."""

    __tablename__ = "pending_staff_access"
    __table_args__ = (UniqueConstraint("email", name="uq_pending_staff_email"),)

    email = Column(String(128), nullable=False, index=True)
    role = Column(String(32), nullable=False, default="sub_admin")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.email = (kwargs.get("email") or "").strip().lower()
        self.role = kwargs.get("role", "sub_admin")
