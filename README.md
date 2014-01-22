# Mirrors

It's some kind of content store.

## Requirements

- Python 3
- Postgres 9.2+
- Some python packages:
 - Django
 - South
 - django-jsonfield
 - ipython
 - pep8
 - psycopg2
 - wsgiref

If you want to have an easier time of it just run `pip install -r
./requirements.txt`. In the future we'll probably make some kind of automated
environment setup.

### Tests
To run the tests just do this:

    $ coverage run --source='.' manage.py test
    $ coverage report
