from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DateTime, CheckConstraint, Enum
from sqlalchemy.orm import relationship

import enum

from .db import Base


class ActionTypesEnum(enum.Enum):
    deposit = 'deposit'
    credit = 'credit'
    transfer = 'transfer'


class Wallet(Base):
    __tablename__ = "wallet"

    id = Column(Integer, primary_key=True, index=True)
    #name = Column(String, unique=True, nullable=False, index=True)
    owner = Column(String, nullable=False)
    balance = Column(DECIMAL(precision=22, scale=4), nullable=False)
    CheckConstraint('balance >= 0', name='balance_check')

    transactions = relationship("Transaction", back_populates="id")


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True)
    to = Column(Integer, ForeignKey('wallet.id'), nullable=False)
    from_ = Column(Integer, ForeignKey('wallet.id'))
    action_type = Column(Enum(ActionTypesEnum), nullable=False)
    date = Column(DateTime, nullable=False)
    amount = Column(DECIMAL, nullable=False)

    wallets = relationship("Wallet", back_populates="transactions")
