## DataScience Hunt

Find videos, tutorials related to DataScience.

### Setup
In postgres console run the following to create database and user.

```sql
CREATE USER dsdb_u WITH PASSWORD 'dsdb_u';
ALTER USER dsdb_u CREATEDB;
CREATE DATABASE dsdb OWNER dsdb_u;
```


For running the server, run the following commands:

```
pipenv shell
pipenv install

python manage.py server
```

