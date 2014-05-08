from flask import Flask, jsonify, render_template, request
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

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