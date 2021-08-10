from datetime import datetime
from decimal import *
from typing import Optional

from sqlalchemy.orm import Session, Query

from . import models


getcontext().prec = 4


def get_wallet(db: Session, wallet_id: int) -> Query:
    return db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()


def get_wallet_by_name(db: Session, owner: str) -> Query:
    return db.query(models.Wallet).filter(models.Wallet.owner == owner).first()


def get_wallets(db: Session, skip: int = 0, limit: int = 100) -> Query:
    return db.query(models.Wallet).offset(skip).limit(limit).all()


def get_wallet_transactions(db: Session, date: str, action_type: str, skip: int = 0, limit: int = 100) -> Query:
    return db.query(models.Transaction).filter(models.Transaction.action_type == action_type and
                                               models.Transaction.date == date)\
        .offset(skip).limit(limit).all()


def create_wallet(db: Session, owner: str) -> models.Wallet:
    db_wallet = models.Wallet(owner=owner, balance=0)
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet


def create_transaction(db: Session, to: Optional[int],
                       from_: Optional[int],
                       action_type: models.ActionTypesEnum,
                       amount: decimal) -> models.Transaction:
    db_transaction = models.Transaction(to=to,
                                        from_=from_,
                                        action_type=action_type,
                                        datetime=datetime.now(),
                                        amount=amount)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def operate_wallet(db: Session,
                   wallet_id: Optional[int],
                   from_: Optional[int],
                   action_type: models.ActionTypesEnum,
                   amount: decimal) -> models.Wallet:

    if action_type == models.ActionTypesEnum.deposit:
        wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id)
        wallet.balance += amount
        create_transaction(db, to=wallet_id, from_=None,
                           action_type=action_type,
                           amount=amount)
    elif action_type == models.ActionTypesEnum.credit:
        wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id)
        wallet.balance -= amount
        create_transaction(db, to=None, from_=from_,
                           action_type=action_type,
                           amount=amount)
    elif action_type == models.ActionTypesEnum.transfer:
        raise SyntaxError
    else:
        raise Exception

    db.commit()
    db.refresh(wallet)
    return wallet


def transfer_money_to_wallet(db: Session,
                             to: int,
                             from_: int,
                             amount: decimal) -> models.Wallet:
    wallet_to = db.query(models.Wallet).filter(models.Wallet.id == to)
    wallet_from = db.query(models.Wallet).filter(models.Wallet.id == from_)

    if wallet_from.balance - amount >= 0:
        wallet_to.balance += amount
        wallet_from.balance -= amount
    else:
        raise ZeroDivisionError

    create_transaction(db, to=to, from_=from_, action_type=models.ActionTypesEnum.transfer, amount=amount)

    db.commit()
    db.refresh(wallet_to)
    db.refresh(wallet_from)

    return wallet_from



