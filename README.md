## DataScience Hunt

Find videos, tutorials related to DataScience.

### Setup

In postgres console(psql or pgadmin) run the following to create database and user.

```sql
CREATE USER dsdb_u WITH PASSWORD 'dsdb_u';
ALTER USER dsdb_u CREATEDB;
CREATE DATABASE dsdb OWNER dsdb_u;
```

---

Then, create virtual env:

```
pip install --upgrade pip pipenv
pipenv shell
```

---
Install all packages:

```
pipenv install
```

---

For running the server, run the following commands:

```
python manage.py migrate

# loads sample data
python manage.py loaddata dshunt/fixtures/*.json 

python manage.py runserver
```

