from setuptools import setup

setup(
    name='MATAHN',
    version='0.2',
    long_description="Download tool for tiled point cloud datasets that delivers a LAZ file with the points inside a bounding box drawn by the user.",
    packages=['matahn'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[	'Flask>=0.10.1'
			,'GeoAlchemy2>=0.2.4'
			,'Jinja2>=2.7.2'
			,'SQLAlchemy>=0.9.4'
			,'celery>=3.1.11'
			,'psycopg2>=2.5.3'
			,'redis>=2.9.1'
			,'requests>=2.2.1'],
    author='Ravi Peters',
    author_email='r.y.peters@tudelft.nl'
)
