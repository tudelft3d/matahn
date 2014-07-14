from matahn import app

from flask import jsonify, render_template, request, abort, redirect, url_for, send_from_directory, send_file
import os, re, datetime

from matahn.models import Tile, Task
from matahn.database import db_session
from matahn.util import get_ewkt_from_bounds

from matahn.tasks import new_task

from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound


@app.route("/")
def matahn():
    return render_template("index.html", max_point_query_size=format_big_number(app.config['MAX_POINT_QUERY_SIZE']))


@app.route("/_getDownloadArea")
def getDownloadArea():
    geojson = db_session.query(func.ST_AsGeoJSON(func.ST_Union(Tile.geom))).one()[0]
    return jsonify(result=geojson)

@app.route("/_getTaskArea")
def getTaskArea():
    #should prob validate this
    task_id = request.args.get('task_id', type=str)
    geojson = db_session.query(func.ST_AsGeoJSON(Task.geom)).filter(Task.id==task_id).one()[0]
    return jsonify(result=geojson)

# these are helper functions that are maybe a bit out of place here
def get_point_count_estimate_from_ewkt(ewkt):
    tiles = db_session.query(   Tile.pointcount \
                                * \
                                func.ST_Area( Tile.geom.ST_Intersection(ewkt) ) / Tile.geom.ST_Area() \
                            ).filter(Tile.geom.intersects(ewkt))
    return sum( [ v[0] for v in tiles ] )
def format_big_number(bignumber):
    if bignumber > 1e9:
        return "{:.0f} billion".format(bignumber/1e9)
    elif bignumber > 1e6:
        return "{:.0f} million".format(bignumber/1e6)
    elif bignumber >1e3:
        return "{:.0f} thousand".format(bignumber/1e3)
    else:
        return "{:.0f}".format(bignumber)

@app.route("/_getPointCountEstimate")
def getPointCountEstimate():
    """Gives an estimate of the number of points in the query rectangle"""
    left = request.args.get('left', type=float)
    bottom = request.args.get('bottom', type=float)
    right = request.args.get('right', type=float)
    top = request.args.get('top', type=float)

    ewkt = get_ewkt_from_bounds(left, bottom, right, top)
    
    total_estimate = get_point_count_estimate_from_ewkt(ewkt)

    return jsonify(result="You selected about {} points!".format(format_big_number(total_estimate)))


@app.route("/_submit")
def submitnewtask():
    left  = request.args.get('left', type=float)
    bottom  = request.args.get('bottom', type=float)
    right  = request.args.get('right', type=float)
    top  = request.args.get('top', type=float)
    email = request.args.get('email', type=str)
    classification = request.args.get('classification', type=str)

    # email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify(wronginput = "Invalid email address")
    # classification validation
    if not re.match(r"^(?=\w{1,2}$)([ug]).*", classification):
        return jsonify(wronginput = "Wrong AHN2 classification")
    # selection bounds validation
    ewkt = get_ewkt_from_bounds(left, bottom, right, top)
    if 0 == db_session.query(Tile).filter( Tile.geom.intersects( ewkt ) ).count():
        return jsonify(wronginput = "Selection is empty")
    if not request.remote_addr in app.config['TRUSTED_IP_ADDRESSES'] and get_point_count_estimate_from_ewkt(ewkt) > app.config['MAX_POINT_QUERY_SIZE']:
        return jsonify(wronginput = "At this time we don't accept requests larger than {} points. Draw a smaller selection to continue.".format(format_big_number(app.config['MAX_POINT_QUERY_SIZE'])))

    # new celery task
    result = new_task.apply_async((left, bottom, right, top, classification))
    # store task parameters in db
    task = Task(id=result.id, ahn2_class=classification, emailto=email, geom=get_ewkt_from_bounds(left, bottom, right, top),\
            time_stamp=datetime.datetime.now(), ip_address=request.remote_addr )
    db_session.add(task)
    db_session.commit()

    taskurl = url_for('tasks_page', task_id=result.id)
    return jsonify(result = taskurl)


@app.route('/tasks/download/<filename>', methods=['GET'])
def tasks_download(filename):
    if app.debug:
        return send_file(app.config['RESULTS_FOLDER'] + filename)


@app.route('/tasks/<task_id>')
def tasks_page(task_id):
    if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', task_id):
        return render_template("tasknotfound.html"), 404
    try:
        task = db_session.query(Task).filter(Task.id == task_id).one()
        task_dict = db_session.query(Task.id, \
                                Task.log_actual_point_count, \
                                Task.log_execution_time, \
                                func.ST_AsText(Task.geom).label('wkt'), \
                                func.ST_XMin(Task.geom).label('minx'), \
                                func.ST_YMin(Task.geom).label('miny'), \
                                func.ST_XMax(Task.geom).label('maxx'), \
                                func.ST_YMax(Task.geom).label('maxy'), \
                                (Task.log_actual_point_count/func.ST_Area(Task.geom)).label('density'), \
                                Task.ahn2_class \
                                ).filter(Task.id==task_id).one().__dict__
    except NoResultFound:
        return render_template("tasknotfound.html"), 404

    status = task.get_status()
    if status == 'SUCCESS':
        filename = app.config['RESULTS_FOLDER'] + task_id + '.laz'
        if (os.path.exists(filename)):
            return render_template("index.html", task = task_dict, status='okay', download_url=task.get_relative_url())
        else:
            return render_template("index.html", task = task_dict, status='deleted')
    elif status == 'PENDING' or status == 'RETRY':
        return render_template("index.html", task = task_dict, status='pending', refresh=True)
    else:
        return render_template("index.html", task = task_dict, status='failure')








