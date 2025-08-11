from database import Base
from sqlalchemy import Column, Integer, Boolean, Text, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import ChoiceType

Status_Choices = (
  ('PENDING','pending'),
  ('IN_TRANSIT','in_transit'),
  ('DELIVERED','delivered'),
)

class User(Base):
  __tablename__ = 'user'

  id  = Column(Integer, primary_key=True)
  username = Column(String(50), unique=True)
  email = Column(String(100), unique=True)
  password= Column(Text)
  is_active = Column(Boolean, default=True)
  is_staff = Column(Boolean, default=False)

  order = relationship('Order', back_populates='user')
  def __repr__(self):
    return f"user {self.username}"


class Order(Base):
  __tablename__ = 'order'

  id = Column(Integer, primary_key=True)
  quantity = Column(Integer)
  status = Column(ChoiceType(Status_Choices), default='PENDING')
  user_id = Column(Integer,ForeignKey('user.id'))
  product_id = Column(Integer, ForeignKey('product.id'))

  user = relationship('User', back_populates='order')
  product = relationship('Product', back_populates='order')
  def __repr__(self):
    return f"order {self.user.username} user"


class Product(Base):
  __tablename__ = 'product'

  id = Column(Integer, primary_key=True)
  name = Column(String(255))
  price = Column(Integer)

  order = relationship('Order', back_populates='product')
  def __repr__(self):
    return f"product {self.order.id} order {self.order.user.username} user"