# The FIP Injection Log sqlite3

Coded to support Python3

## Getting Started
- Install Python3
- Install Dependencies:

`pip install -r requirements.txt`

- Create a new file `secure_settings.py` in the root directory
- Set your `EMAIL_HOST_PASSWORD` and `SECRET_KEY values`.
- `EMAIL_HOST_USER` and `EMAIL_HOST` will also need to be changed in the `secure_settings.py` file


To setup the database, use the standard Django protocol:

`python manage.py makemigrations`

`python manage.py migrate`

Note: a superuser needs to be created for the django database.  a `WarriorAdmin` group also needs to be created

Run the server:

`python manage.py runserver`
