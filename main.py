from fastapi import Depends, FastAPI, HTTPException

from sqlalchemy.orm import Session

from src import crud, schemas, models
from src.db import SessionLocal, engine

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
def create_user(wallet: schemas.WalletCreate, db: Session = Depends(get_db)):
    db_wallet = crud.get_wallet_by_name(db, name=wallet.name)
    if db_wallet:
        raise HTTPException(status_code=400, detail="Wallet already registered")
    return crud.create_wallet(db=db, owner=wallet.owner, name=wallet.name)


@app.get('/add_wallet')
async def add_wallet(user: str):
    ...
    return {'message': f'Wallet for user {user} added.'}
