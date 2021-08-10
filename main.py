from fastapi import Depends, FastAPI, HTTPException

from typing import List, Optional

from decimal import Decimal

from sqlalchemy.orm import Session

from src import crud, schemas, models
from src.db import SessionLocal, engine
from src.app_exceptions import LowerThanZeroBalanceException


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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
    return crud.create_wallet(db=db, owner=wallet.owner, name=wallet.name)


@app.get("/wallets/", response_model=List[schemas.Wallet])
def read_wallets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    wallets = crud.get_wallets(db=db, skip=skip, limit=limit)
    return wallets


@app.get("/wallets/{wallet_id}", response_model=schemas.Wallet)
def read_wallet(wallet_id: int, db: Session = Depends(get_db)):
    wallet = crud.get_wallet_by_id(db=db, wallet_id=wallet_id)
    return wallet


@app.get("/wallets/name/{wallet_name}", response_model=schemas.Wallet)
def read_wallet(wallet_name: str, db: Session = Depends(get_db)):
    wallet = crud.get_wallet_by_name(db=db, name=wallet_name)
    print(wallet)
    return wallet


@app.get("/wallets/transactions/", response_model=List[schemas.Transaction])
def read_transactions(date: str,
                      action_type: models.ActionTypesEnum,
                      skip: int = 0,
                      limit: int = 100,
                      db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db=db, action_type=action_type, date=date, skip=skip, limit=limit)
    return transactions


@app.put("/wallets/increase", response_model=schemas.Wallet)
def increase_wallet_balance(wallet_id: Optional[int],
                            amount: Decimal,
                            db: Session = Depends(get_db)):
    changed_wallet = crud.increase_wallet_balance(db=db, wallet_id=wallet_id, amount=amount)
    return changed_wallet


@app.put("/wallets/decrease", response_model=schemas.Wallet)
def decrease_wallet_balance(wallet_id: Optional[int],
                            amount: Decimal,
                            db: Session = Depends(get_db)):
    try:
        changed_wallet = crud.decrease_wallet_balance(db=db, wallet_id=wallet_id, amount=amount)
    except LowerThanZeroBalanceException as exception:
        raise HTTPException(status_code=400, detail=str(exception))

    return changed_wallet


@app.put("/wallets/transfer_money", response_model=List[schemas.Wallet])
def transfer_money(to: int,
                   from_: int,
                   amount: Decimal,
                   db: Session = Depends(get_db)):
    try:
        wallets = crud.transfer_money_to_wallet(db=db, to=to, from_=from_, amount=amount)
    except LowerThanZeroBalanceException as exeption:
        raise HTTPException(status_code=400, detail=str(exeption))

    return wallets
