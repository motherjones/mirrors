from setuptools import setup, find_packages

setup(name='mirrors',
    version=__import__('mirrors').__version__,
    packages=find_packages(exclude=['sample_project']),
    install_requires=[
        'South>=0.8.4',
        'jsonfield>=0.9.20',
        'djangorestframework>=2.3.12'
    ],
    extras_require = {
        'development': ['Sphinx>=1.2.1', 'coverage'],
    },   
    #TODO: Add description, license, and classifiers
    # PyPI stuff, if the time ever comes
    author='Mikela Clemmons, Jon Friedman',
    author_email='mclemmons@motherjones.com, jfriedman@motherjones.com',
    long_description=open('README.md').read())
