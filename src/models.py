import enum
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Numeric, Date

from .db import Base


class ActionTypesEnum(enum.Enum):
    deposit = 'deposit'
    withdrawal = 'withdrawal'
    transfer = 'transfer'


class Wallet(Base):
    __tablename__ = "wallet"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    owner = Column(String, nullable=False)
    balance = Column(Numeric(precision=12, scale=4), nullable=False)


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True)
    to = Column(Integer, ForeignKey('wallet.id'), nullable=False)
    from_ = Column(Integer, ForeignKey('wallet.id'))
    action_type = Column(Enum(ActionTypesEnum), nullable=False)
    transaction_date = Column(Date, nullable=False, default=datetime.date(datetime.today()))
    amount = Column(Numeric(precision=100, scale=4), nullable=False)
