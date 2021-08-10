import json
from datetime import datetime

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class Wallet:
    def __init__(self):
        self.id = 1
        self.name = 'test'
        self.owner = 'test'
        self.balance = 0.001
        self.data = {
            'name': self.name,
            'owner': self.owner,
            'balance': self.balance
        }
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.transactions = [
            {
                "id": 1,
                "to": 1,
                "from_": 1,
                "action_type": "deposit",
                "transaction_date": "2021-08-11",
                "amount": 0.001
            },
            {
                "id": 2,
                "to": 1,
                "from_": 1,
                "action_type": "withdrawal",
                "transaction_date": "2021-08-11",
                "amount": 0.001
            },
            {
                "id": 3,
                "to": 1,
                "from_": 2,
                "action_type": "transfer",
                "transaction_date": "2021-08-11",
                "amount": 0.001
            }
        ]

    def get_response(self):
        return {
            'id': self.id,
            'name': self.name,
            'owner': self.owner,
            'balance': self.balance
        }


wallet1 = Wallet()
wallet2 = Wallet()


def test_create_wallet():
    response = client.post('/wallets/', data=json.dumps(wallet1.data), headers=wallet1.headers)

    assert response.status_code == 200
    assert response.json() == wallet1.get_response()

    response = client.post('/wallets/', data=json.dumps(wallet1.get_response()))
    assert response.status_code == 400
    assert response.json() == {'detail': 'Wallet already registered'}


def test_read_wallets():
    response = client.get('/wallets/')
    assert response.status_code == 200
    assert wallet1.get_response() in response.json()


def test_read_wallet_by_id():
    response = client.get(f'/wallets/{wallet1.id}')

    assert response.status_code == 200
    assert response.json() == wallet1.get_response()


def test_read_wallet_by_name():
    response = client.get(f'/wallets/name/{wallet1.name}')
    assert response.status_code == 200
    assert response.json() == wallet1.get_response()


def test_increase_wallet_balance():
    response = client.put(f'/wallets/increase?wallet_id={wallet1.id}&amount=0.001')
    assert response.status_code == 200

    wallet1.balance += 0.001

    assert response.json() == wallet1.get_response()


def test_decrease_wallet_balance():
    response = client.put(f'/wallets/decrease?wallet_id={wallet1.id}&amount=0.001')

    assert response.status_code == 200

    wallet1.balance -= 0.001

    assert response.json() == wallet1.get_response()


def test_transfer_money():
    # Wallet2 creation is necessary for future tests
    wallet2.id += 1
    wallet2.name = 'new_test'
    wallet2.data['id'] = wallet2.id
    wallet2.data['name'] = wallet2.name

    response = client.post('/wallets/', data=json.dumps(wallet2.data), headers=wallet2.headers)

    assert response.status_code == 200

    wallet1.balance += 0.001
    wallet2.balance -= 0.001

    response = client.put(f'/wallets/transfer_money?to={wallet1.id}&from_={wallet2.id}&amount=0.001')

    assert response.status_code == 200

    new_wallet1, new_wallet2 = response.json()

    assert new_wallet1 == wallet1.get_response()
    assert new_wallet2 == wallet2.get_response()

    response = client.put(f'/wallets/transfer_money?to={wallet1.id}&from_={wallet2.id}&amount=0.001')

    assert response.status_code == 400
    assert response.json() == {'detail': 'Balance could not be lower than zero'}

    response = client.put(f'/wallets/transfer_money?to={wallet1.id}&from_=1000&amount=0.001')

    assert response.status_code == 400
    assert response.json() == {'detail': 'There is no such wallet'}

    response = client.put(f'/wallets/transfer_money?to=1000&from_={wallet2.id}&amount=0.001')

    assert response.status_code == 400
    assert response.json() == {'detail': 'There is no such wallet'}

    response = client.put(f'/wallets/transfer_money?to=1000&from_=100&amount=0.001')

    assert response.status_code == 400
    assert response.json() == {'detail': 'There is no such wallet'}


def test_read_transactions():
    responses = []

    response1 = client.get(f'/wallets/transactions/?transaction_date={str(datetime.date(datetime.today()))}'
                           f'&action_type=deposit&skip=0&limit=100')

    assert response1.status_code == 200

    responses.append(response1.json()[0])

    response2 = client.get(f'/wallets/transactions/?transaction_date={str(datetime.date(datetime.today()))}'
                           f'&action_type=withdrawal&skip=0&limit=100')

    assert response2.status_code == 200

    responses.append(response2.json()[0])

    response3 = client.get(f'/wallets/transactions/?transaction_date={str(datetime.date(datetime.today()))}'
                           f'&action_type=transfer&skip=0&limit=100')

    assert response3.status_code == 200

    responses.append(response3.json()[0])

    assert responses == wallet1.transactions
