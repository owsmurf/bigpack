python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

`PGHOST` `localhost`
`PGPORT` `5432`
`PGDATABASE` `bigpack`
`PGUSER` `postgres`
`PGPASSWORD` `postgres`

data import
python db/03_import_data.py

app launch
python run.py

unit-tests
python -m unittest tests.test_calculation -v