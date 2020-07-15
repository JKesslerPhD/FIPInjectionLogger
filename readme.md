# The FIP Injection Log

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

Note: a superuser needs to be created for the django database.  A ``WarriorAdmin`user group also needs to be created in the database before you can run the program.  

Run the server:

`python manage.py runserver`

Create the `WarriorAdmin` user group by using the Django admin interface (`/admin`).
