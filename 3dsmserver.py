from flask import Flask, jsonify, render_template, request
import os
import uuid
import time

ROOT_FOLDER        = '/Users/hugo/www/webahn/'
TASKS_FOLDER       = ROOT_FOLDER + 'tasks/'
RESULTS_FOLDER     = ROOT_FOLDER + 'results/'

app = Flask(__name__, static_url_path='')
app.config['TASKS_FOLDER']   = TASKS_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")



@app.route("/matahn", methods=['GET', 'POST'])
def matahn():
    if request.method == 'POST':
        e = session['useremail']
        print e
        return redirect(url_for('/matahn'))
    return render_template("matahn/index.html")


@app.route("/_getPointCountEstimate")
def getPointCountEstimate():
	"""Gives an inaccurate estimate of the number of points in the query rectangle"""
	ll_x = request.args.get('ll_x', type=float)
	ll_y = request.args.get('ll_y', type=float)
	ur_x = request.args.get('ur_x', type=float)
	ur_y = request.args.get('ur_y', type=float)
	d_x = ur_x - ll_x
	d_y = ur_y - ll_y
	density = 15
	return jsonify(result="You selected about {:.0f} points!".format(d_x*d_y*density))

if __name__ == "__main__":
	app.run(host='0.0.0.0',debug=True)