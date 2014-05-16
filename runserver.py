# see http://flask.pocoo.org/docs/patterns/appdispatch/

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from matahn import app as matahn_app
from frontend import app as frontend_app

application = DispatcherMiddleware( frontend_app, {
    '/matahn':     matahn_app
})

run_simple('localhost', 5000, application, use_reloader=True)


