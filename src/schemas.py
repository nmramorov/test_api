from datetime import date
from decimal import *

from pydantic import BaseModel

from src.models import ActionTypesEnum

getcontext().prec = 4
getcontext().rounding = 'ROUND_FLOOR'


class WalletBase(BaseModel):
    name: str
    owner: str
    balance: Decimal


class WalletCreate(WalletBase):
    pass


class Wallet(WalletBase):
    id: int

    class Config:
        orm_mode = True


class TransactionBase(BaseModel):
    id: int
    to: int
    from_: int
    action_type: ActionTypesEnum
    date: date
    amount: Decimal


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    class Config:
        orm_mode = True
