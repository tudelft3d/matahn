from matahn import app

from flask import jsonify, render_template, request, abort, redirect, url_for
import os
import uuid
import time

from matahn.models import Tile
from matahn.database import db_session
from matahn.util import get_ewkt_from_bounds

from matahn import tasks

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

    result = tasks.merge_tiles.delay(left, bottom, right, top, classification)

    return jsonify( result=url_for('request_download', task_id=result.id) )


@app.route("/request_download/<task_id>")
def request_download(task_id):    
    result = tasks.merge_tiles.AsyncResult(task_id)

    # note this is not the way to serve static files! this should really happen outside of flask (ie redirect the user to a path that is handled by a static file server)
    if result.status == 'SUCCESS':
        return redirect( app.config['DOWNLOAD_URL_PATH']+result.result['filename'] )
    else:
        abort(404)