from setuptools import setup, find_packages

setup(name='mirrors',
      version=__import__('mirrors').__version__,
      packages=find_packages(),
      install_requires=[
          'Django>=1.6.1',
          'South>=0.8.4',
          'coverage>=3.7.1',
          'django-jsonfield>=0.9.12',
          'psycopg2>=2.5.2',
          'Sphinx>=1.2.1',
          'djangorestframework>=2.3.12'
      ],

      # PyPI stuff, if the time ever comes
      author='Mikela Clemmons, Jon Friedman',
      author_email='mclemmons@motherjones.com, jfriedman@motherjones.com')
