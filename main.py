from datetime import date
from decimal import Decimal, getcontext
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from src import crud, schemas, models
from src.app_exceptions import LowerThanZeroBalanceException
from src.db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

getcontext().prec = 4
getcontext().rounding = 'ROUND_FLOOR'


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/wallets/", response_model=schemas.Wallet)
def create_wallet(wallet: schemas.WalletCreate, db: Session = Depends(get_db)):
    db_wallet = crud.get_wallet_by_name(db, name=wallet.name)
    if db_wallet:
        raise HTTPException(status_code=400, detail="Wallet already registered")
    return crud.create_wallet(db=db, owner=wallet.owner, name=wallet.name, balance=Decimal(wallet.balance))


@app.get("/wallets/", response_model=List[schemas.Wallet])
def read_wallets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    wallets = crud.get_wallets(db=db, skip=skip, limit=limit)
    return wallets


@app.get("/wallets/{wallet_id}", response_model=schemas.Wallet)
def read_wallet(wallet_id: int, db: Session = Depends(get_db)):
    db_wallet = crud.get_wallet_by_id(wallet_id=wallet_id, db=db)
    if not db_wallet:
        raise HTTPException(status_code=400, detail='There is no such wallet')
    return db_wallet


@app.get("/wallets/name/{wallet_name}", response_model=schemas.Wallet)
def read_wallet(wallet_name: str, db: Session = Depends(get_db)):
    wallet = crud.get_wallet_by_name(db=db, name=wallet_name)

    return wallet if wallet else HTTPException(status_code=400, detail='There is no such wallet')


@app.get("/wallets/transactions/", response_model=List[schemas.Transaction])
def read_transactions(transaction_date: str,
                      action_type: models.ActionTypesEnum,
                      skip: int = 0,
                      limit: int = 100,
                      db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db=db, action_type=action_type,
                                         transaction_date=date.fromisoformat(transaction_date.strip('"')),
                                         skip=skip,
                                         limit=limit)
    return transactions if transactions else HTTPException(status_code=400,
                                                           detail='There are no such transactions')


@app.put("/wallets/increase", response_model=schemas.Wallet)
def increase_wallet_balance(wallet_id: Optional[int],
                            amount: str,
                            db: Session = Depends(get_db)):
    wallet = crud.get_wallet_by_id(db=db, wallet_id=wallet_id)
    if not wallet:
        raise HTTPException(status_code=400, detail='There is no such wallet')

    changed_wallet = crud.increase_wallet_balance(db=db, wallet_id=wallet_id, amount=Decimal(amount))
    return changed_wallet


@app.put("/wallets/decrease", response_model=schemas.Wallet)
def decrease_wallet_balance(wallet_id: Optional[int],
                            amount: str,
                            db: Session = Depends(get_db)):
    wallet = crud.get_wallet_by_id(db=db, wallet_id=wallet_id)
    if not wallet:
        raise HTTPException(status_code=400, detail='There is no such wallet')

    try:
        changed_wallet = crud.decrease_wallet_balance(db=db, wallet_id=wallet_id, amount=Decimal(amount))
    except LowerThanZeroBalanceException as exception:
        raise HTTPException(status_code=400, detail=str(exception))

    return changed_wallet


@app.put("/wallets/transfer_money", response_model=List[schemas.Wallet])
def transfer_money(to: int,
                   from_: int,
                   amount: str,
                   db: Session = Depends(get_db)):
    wallet_to = crud.get_wallet_by_id(db=db, wallet_id=to)
    wallet_from = crud.get_wallet_by_id(db=db, wallet_id=from_)
    if not wallet_to or not wallet_from:
        raise HTTPException(status_code=400, detail='There is no such wallet')

    try:
        wallets = crud.transfer_money_to_wallet(db=db, to=to, from_=from_, amount=Decimal(amount))
    except LowerThanZeroBalanceException as exception:
        raise HTTPException(status_code=400, detail=str(exception))

    return wallets
