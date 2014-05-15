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



# @app.route("/matahn", methods=['GET', 'POST'])
# def matahn():
#     if request.method == 'POST':
#         e = session['useremail']
#         print e
#         return redirect(url_for('/matahn'))
#     return render_template("matahn/index.html")

@app.route("/matahn")
def matahn():
    return render_template("matahn/index.html")


@app.route("/matahn/_getPointCountEstimate")
def getPointCountEstimate():
    """Gives an inaccurate estimate of the number of points in the query rectangle"""
    ll_x = request.args.get('ll_x', type=float)
    ll_y = request.args.get('ll_y', type=float)
    ur_x = request.args.get('ur_x', type=float)
    ur_y = request.args.get('ur_y', type=float)
    d_x = ur_x - ll_x
    d_y = ur_y - ll_y
    density = 15
    total = d_x * d_y * density
    if (total > 1e6):
        return jsonify(result="You selected about {:.0f}M points!".format(d_x*d_y*density/1e6))
    else:
        return jsonify(result="You selected about {:.0f}k points!".format(d_x*d_y*density/1e3))



@app.route("/matahn/_submit")
def submitnewtask():
    ll_x  = request.args.get('ll_x', type=float)
    ll_y  = request.args.get('ll_y', type=float)
    ur_x  = request.args.get('ur_x', type=float)
    ur_y  = request.args.get('ur_y', type=float)
    email = request.args.get('email', '')
    classification = request.args.get('classification', '')
    jid = str(uuid.uuid4()).split('-')[0]
    fjob = open("%s%s.txt" % (TASKS_FOLDER, jid), 'w')
    fjob.write("ll_x: %s\n" % ll_x)
    fjob.write("ll_t: %s\n" % ll_y)
    fjob.write("ur_x: %s\n" % ur_x)
    fjob.write("ur_y: %s\n" % ur_y)
    fjob.write("classification: %s\n" % classification)
    fjob.write("%s\n" % email)
    fjob.write("%s\n" % time.asctime())
    fjob.close()
    return jsonify(result=jid)

if __name__ == "__main__":
	app.run(debug=True)