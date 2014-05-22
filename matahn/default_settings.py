DEBUG			= True

SQLALCHEMY_DATABASE_URI = 'postgresql://matahn:matahn@localhost/matahn'

RESULTS_FOLDER 	= '/data/matahn/results/'

BLADINDEX_JSON = '/home/ravipeters/git/webahn/tiles.json'

LASINFO_BINARY = '/usr/local/bin/lasinfo'
LASMERGE_BINARY = '/usr/local/bin/lasmerge'

CELERY_BROKER_URL = 'redis://localhost:6379/0',
CELERY_RESULT_BACKEND = 'db+'+SQLALCHEMY_DATABASE_URI
