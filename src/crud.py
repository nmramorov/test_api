from decimal import *
from typing import Optional, List

from sqlalchemy.orm import Session, Query

from . import models, app_exceptions

getcontext().prec = 4
getcontext().rounding = 'ROUND_FLOOR'


def get_wallet_by_id(db: Session, wallet_id: int) -> Query:
    return db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()


def get_wallet_by_name(db: Session, name: str) -> Query:
    return db.query(models.Wallet).filter(models.Wallet.name == name).first()


def get_wallets(db: Session, skip: int = 0, limit: int = 100) -> Query:
    return db.query(models.Wallet).offset(skip).limit(limit).all()


def get_transactions(db: Session, date: str, action_type: models.ActionTypesEnum, skip: int = 0,
                     limit: int = 100) -> Query:
    return db.query(models.Transaction).filter(models.Transaction.action_type == action_type and
                                               models.Transaction.date == date) \
        .offset(skip).limit(limit).all()


def create_wallet(db: Session, owner: str, name: str, balance: Decimal = 0) -> models.Wallet:
    db_wallet = models.Wallet(owner=owner, name=name, balance=balance)
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet


def create_transaction(db: Session, to: Optional[int],
                       from_: Optional[int],
                       action_type: models.ActionTypesEnum,
                       amount: Decimal) -> models.Transaction:
    db_transaction = models.Transaction(to=to,
                                        from_=from_,
                                        action_type=action_type,
                                        amount=amount)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def increase_wallet_balance(db: Session,
                            wallet_id: Optional[int],
                            amount: Decimal) -> models.Wallet:
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    wallet.balance += amount

    create_transaction(db=db,
                       to=wallet_id,
                       from_=wallet_id,
                       action_type=models.ActionTypesEnum.deposit,
                       amount=amount)
    db.commit()
    db.refresh(wallet)
    return wallet


def decrease_wallet_balance(db: Session,
                            wallet_id: Optional[int],
                            amount: Decimal) -> models.Wallet:
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if wallet.balance - amount < 0:
        raise app_exceptions.LowerThanZeroBalanceException

    wallet.balance -= amount

    create_transaction(db=db, to=wallet_id,
                       from_=wallet_id,
                       action_type=models.ActionTypesEnum.withdrawal,
                       amount=amount)

    db.commit()
    db.refresh(wallet)
    return wallet


def transfer_money_to_wallet(db: Session,
                             to: int,
                             from_: int,
                             amount: Decimal) -> List[models.Wallet]:
    wallet_to = db.query(models.Wallet).filter(models.Wallet.id == to).first()
    wallet_from = db.query(models.Wallet).filter(models.Wallet.id == from_).first()

    if wallet_from.balance - amount >= 0:
        wallet_to.balance += amount
        wallet_from.balance -= amount
    else:
        raise app_exceptions.LowerThanZeroBalanceException

    create_transaction(db, to=to, from_=from_, action_type=models.ActionTypesEnum.transfer, amount=amount)

    db.commit()
    db.refresh(wallet_to)
    db.refresh(wallet_from)

    return [wallet_to, wallet_from]
