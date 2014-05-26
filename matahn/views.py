from matahn import app

from flask import jsonify, render_template, request, abort, redirect, url_for, send_from_directory
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
    email = request.args.get('email', type=str)
    classification = request.args.get('classification', type=str)
    
    #TODO: validate string inputs

    result = tasks.merge_tiles.delay(left, bottom, right, top, classification)
    taskurl =  url_for('matahn') + ('tasks/%s' % result.id)
    return jsonify(result = taskurl)
    # return jsonify( result=url_for('matah'), task_id=result.id) )


@app.route('/tasks/download/<task_id>')
def tasks_download(task_id):
    return send_from_directory(app.config['DOWNLOAD_URL_PATH'], '%s.laz' % task_id)


@app.route('/hugo/<ledoux>')
def hugo_page(ledoux): 
    return render_template("downloadpage.html", taskid = ledoux, success = True)

@app.route('/tasks/<task_id>')
def tasks_page(task_id): 
    print "task_id", task_id   
    result = tasks.merge_tiles.AsyncResult(task_id)
    if result.status == 'SUCCESS':
        print "success"
        return render_template("downloadpage.html", taskid = task_id, success = True)
    else:
        print "failure"
        return render_template("downloadpage.html", taskid = task_id, success = False)


    # if result.status == 'SUCCESS':
    #     return redirect( app.config['DOWNLOAD_URL_PATH']+result.result['filename'] )
    # else:
    #     abort(404)
