from setuptools import setup, find_packages

setup(name='mirrors',
      version=__import__('mirrors').__version__,
      packages=find_packages(exclude=['sample_project']),
      install_requires=[
          'Django>=1.6.1',
          'South>=0.8.4',
          'coverage>=3.7.1',
          'psycopg2>=2.5.2',
          'Sphinx>=1.2.1',
          'jsonfield>=0.9.20',
          'djangorestframework>=2.3.12'
          'djangorestframework>=2.3.12',
          'jsonfield'
      ],
      #TODO: Add description, license, and classifiers
      # PyPI stuff, if the time ever comes
      author='Mikela Clemmons, Jon Friedman',
      author_email='mclemmons@motherjones.com, jfriedman@motherjones.com',
      long_description=open('README.md').read())
