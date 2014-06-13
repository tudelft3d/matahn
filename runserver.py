# see http://flask.pocoo.org/docs/patterns/appdispatch/

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from matahn import app as matahn_app

application = DispatcherMiddleware( matahn_app )

if __name__ == '__main__':
    run_simple('localhost', 5000, application, use_reloader=True)


