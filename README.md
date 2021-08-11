## Test app for EPAM

### Build

Clone the repo and run ``
docker-compose up -d``.  
To run DB separately, comment the "app" section in docker-compose.yml file.
Then run ``uvicorn main:app --reload `` in the terminal prompt.

### Access API

Go to 0.0.0.0/docs to observe the API

### Tests

To run tests, enable only Postgres (f.e by commenting "app" part in docker-compose.yml).  
Run ``pytest`` then.