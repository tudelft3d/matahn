from matahn import app

from flask import jsonify, render_template, request
import os
import uuid
import time

from matahn.models import Tile
from matahn.database import db_session

from sqlalchemy import func

# @app.route("/matahn", methods=['GET', 'POST'])
# def matahn():
#     if request.method == 'POST':
#         e = session['useremail']
#         print e
#         return redirect(url_for('/matahn'))
#     return render_template("matahn/index.html")

@app.route("/")
def matahn():
    return render_template("index.html")


@app.route("/_getDownloadArea")
def getDownloadArea():
    geojson = db_session.query(func.ST_AsGeoJSON(func.ST_Union(Tile.geom))).one()[0]

    return jsonify(result=geojson)


@app.route("/_getPointCountEstimate")
def getPointCountEstimate():
    """Gives an estimate of the number of points in the query rectangle"""
    left = request.args.get('left', type=float)
    bottom = request.args.get('bottom', type=float)
    right = request.args.get('right', type=float)
    top = request.args.get('top', type=float)

    ewkt = get_ewkt_from_bounds(left, bottom, right, top)

    tiles = db_session.query(   Tile.pointcount \
                                * \
                                func.ST_Area( Tile.geom.ST_Intersection(ewkt) ) / Tile.geom.ST_Area() \
                            ).filter(Tile.geom.intersects(ewkt))
    
    total_estimate = sum( [ v[0] for v in tiles ] )

    if total_estimate > 1e6:
        return jsonify(result="You selected about {:.0f} million points!".format(total_estimate/1e6))
    elif total_estimate >1e3:
        return jsonify(result="You selected about {:.0f} thousand points!".format(total_estimate/1e3))
    else:
        return jsonify(result="You selected about {:.0f} points!".format(total_estimate))


@app.route("/_submit")
def submitnewtask():
    left  = request.args.get('left', type=float)
    bottom  = request.args.get('bottom', type=float)
    right  = request.args.get('right', type=float)
    top  = request.args.get('top', type=float)
    email = request.args.get('email', '')
    classification = request.args.get('classification', '')
    jid = str(uuid.uuid4()).split('-')[0]
    fjob = open("%s%s.txt" % (app.config['TASKS_FOLDER'], jid), 'w')
    fjob.write("left: %s\n" % left)
    fjob.write("ll_t: %s\n" % bottom)
    fjob.write("right: %s\n" % right)
    fjob.write("top: %s\n" % top)
    fjob.write("classification: %s\n" % classification)
    fjob.write("%s\n" % email)
    fjob.write("%s\n" % time.asctime())
    fjob.close()
    return jsonify(result=jid)


def get_ewkt_from_bounds(x_min, y_min, x_max, y_max):
    return 'SRID=28992;POLYGON(({0} {1}, {2} {1}, {2} {3}, {0} {3}, {0} {1}))'.format(x_min, y_min, x_max, y_max)