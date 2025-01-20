from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship

from backend.utils.database import Base

class Order(Base):
    """ORM model for orders"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, nullable=False, index=True)
    table_number = Column(Integer, nullable=False)
    customer_name = Column(String(100), nullable=False)
    is_group_order = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False, default="initialized")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="orders")

    # Constraints
    __table_args__ = (
        CheckConstraint('table_number >= 1 AND table_number <= 10', name='check_table_number_range'),
        CheckConstraint(
            "status IN ('initialized', 'in_progress', 'confirmed', 'completed', 'cancelled')",
            name='check_valid_status'
        ),
    )

    def __init__(self, **kwargs):
        if 'table_number' in kwargs and (kwargs['table_number'] < 1 or kwargs['table_number'] > 10):
            raise ValueError("Table number must be between 1 and 10")
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Order {self.order_number}>"

    def to_dict(self):
        """Convert order to dictionary"""
        return {
            "id": self.id,
            "order_number": self.order_number,
            "table_number": self.table_number,
            "customer_name": self.customer_name,
            "is_group_order": self.is_group_order,
            "user_id": self.user_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 