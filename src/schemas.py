from decimal import Decimal

from pydantic import BaseModel

from src.models import ActionTypesEnum


class WalletBase(BaseModel):
    id: int
    name: str
    owner: str
    balance: Decimal


class WalletCreate(WalletBase):
    pass


class Wallet(WalletBase):

    class Config:
        orm_mode = True


class TransactionBase(BaseModel):
    id: int
    to: int
    from_: int
    action_type: ActionTypesEnum
    datetime: str
    amount: Decimal


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    class Config:
        orm_mode = True
