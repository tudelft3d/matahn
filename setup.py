from setuptools import setup

setup(
    name='MATAHN',
    version='0.1',
    long_description="Download tool for AHN2 that delivers a LAZ file with the points inside a bounding box drawn by the user.",
    packages=['matahn'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[	'Flask>=0.10.1'
						,'GeoAlchemy2>=0.2.4'
						,'Jinja2>=2.7.2'
						,'MarkupSafe>=0.23'
						,'SQLAlchemy>=0.9.4'
						,'Werkzeug>=0.9.4'
						,'amqp>=1.4.5'
						,'anyjson>=0.3.3'
						,'billiard>=3.3.0.17'
						,'celery>=3.1.11'
						,'itsdangerous>=0.24'
						,'kombu>=3.0.16'
						,'psycopg2>=2.5.3'
						,'pytz>=2014.3'
						,'redis>=2.9.1'
						,'requests>=2.2.1'
						,'subprocess32>=3.2.6'
						,'wsgiref>=0.1.2' ],
	author='Ravi Peters',
    author_email='r.y.peters@tudelft.nl'
)