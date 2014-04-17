# Mirrors

Mirrors is the back end (or content repository, if you will) django application
for the [Smoke](https://github.com/benbreedlove/smokejs) and
[Mirrors](https://github.com/motherjones/mirrors_server) project.

## Requirements

* Postgres 9.2+
* Python 3.2
    * django 1.6
    * django rest framework
    * south
    * psycopg2
    * sphinx

## Installation

Installation is easy:

```bash
cd /path/to/mirrors
pip install -e ./
```

### Testing

To run the tests enter these commands:

```bash
cd sample_project
python manage.py test mirrors
```

## Documentation

The actual docs can be found at http://motherjones.github.io/mirrors/ and in
the docs directory of this project. Just run `make` inside of it and it'll
build you a nice, readable version of our API.
    
