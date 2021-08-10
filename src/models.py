from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DateTime, CheckConstraint, Enum

from datetime import datetime

import enum

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
    balance = Column(DECIMAL(precision=22, scale=4), nullable=False)
    CheckConstraint('balance >= 0', name='balance_check')


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True)
    to = Column(Integer, ForeignKey('wallet.id'), nullable=False)
    from_ = Column(Integer, ForeignKey('wallet.id'))
    action_type = Column(Enum(ActionTypesEnum), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.now())
    amount = Column(DECIMAL, nullable=False)
