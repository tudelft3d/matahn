# see http://flask.pocoo.org/docs/patterns/appdispatch/


from matahn import app as matahn_app

if __name__ == '__main__':
	matahn_app.run(port=5050)

