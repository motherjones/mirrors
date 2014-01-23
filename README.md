# Mirrors

It's some kind of content store.

## Requirements

- Python 3
- Postgres 9.2+
- Some python packages:
 - Django
 - South
 - django-jsonfield
 - psycopg2
 - Sphinx

If you want to have an easier time of it just run `pip install -r
./requirements.txt`. In the future we'll probably make some kind of automated
environment setup.

## Running

Before doing anything other than installing all of the requirements, remember to
set up your database. Edit `mirrors/settings.py` to reflect your database
settings and then do this:

    $ python ./manage.py syncdb
      [...]
    $ python ./manage.py migrate

## Tests
To run the tests just do this:

    $ coverage run --source='.' --omit='*migrations*' manage.py test
    $ coverage report
