from fastapi import FastAPI


app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'This is test task created by Mramorov Nikita for EPAM.'}


@app.get('/add_wallet')
async def add_wallet(user: str):
    ...
    return {'message': f'Wallet for user {user} added.'}
