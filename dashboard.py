from flask import render_template, request, jsonify
from models import app, db, tg_ioc, host_binary, host_ioc, tg_binary, host_guid
from sqlalchemy import func
import datetime
import time

@app.route('/_get_iocs')
def get_iocs():
    order = 'sum ' + request.args.get('sSortDir_0', 'desc')
    sum_by = request.args.get('sSumBy', 'severity')

    if sum_by == 'host_count':
        query = db.session.query(tg_ioc.title, func.count(host_binary.host_guid).label('sum'), tg_ioc.id). \
                join(host_ioc).join(host_binary).group_by(tg_ioc.id).order_by(order)
    elif sum_by == 'severity':
        query = db.session.query(tg_ioc.title, tg_ioc.severity.label('sum'), tg_ioc.id). \
                join(host_ioc).join(host_binary).group_by(tg_ioc.id).order_by(order)
    return get_datatable_items(query)

@app.route('/_get_host_binaries')
def get_host_binaries():
    order = 'sum ' + request.args.get('sSortDir_0', 'desc')
    sum_by = request.args.get('sSumBy', 'severity')

    if sum_by == 'ioc_count':
        query = db.session.query(host_guid.host_name, func.count(tg_ioc.id).label('sum'), host_binary.host_guid). \
                join(host_binary).join(host_ioc).join(tg_ioc).group_by(host_binary.host_guid).order_by(order)
    elif sum_by == 'severity':
        query = db.session.query(host_guid.host_name, func.sum(tg_ioc.severity).label('sum'), host_binary.host_guid). \
                join(host_binary).join(host_ioc).join(tg_ioc).group_by(host_binary.host_guid).order_by(order)
    return get_datatable_items(query)

def apply_filters(query, exec_date):
    if exec_date:
        try:
            dt = datetime.datetime.strptime(exec_date, '%m/%d/%Y')
            query = query.filter(host_binary.execution_time >= dt)
        except ValueError:
            pass
    return query

def get_datatable_items(query):
    # filtering logic
    exec_date = request.args.get('sExecDate', '')
    #ioc_list  = request.args.get('sIocs', '')
    #host_list = request.args.get('sHosts', '')
    #categ_list  = request.args.get('sCategories', '')
    #sever_list = request.args.get('sSeverities', '')
    #conf_list = request.args.get('sConfidences', '')

    # record count before filtering
    count = query.count()

    start = int(request.args.get('iDisplayStart', 0))
    limit = int(request.args.get('iDisplayLength', 10))

    query = apply_filters(query, exec_date)
    print query
    filtered_count = query.count()
    results = query.limit(limit).offset(start).all()
    # everything sent as text
    rows = [[str(it) for it in list(r)] for r in results]
    d = {   'sEcho':request.args.get('sEcho',0),
            'iTotalRecords':count,
            'iTotalDisplayRecords':filtered_count,
            'aaData':rows}
    return jsonify(d)

'''
Creates list of results, formatting the date at given index
'''
def process_date(results, ind):
    for row in results:
        if type(row[ind]) == datetime.datetime:
            row[ind] = row[ind].strftime("%Y-%m-%d") 
    return results

@app.route('/_get_ioc_details')
def get_ioc_details():
    keyId = request.args.get('keyId', 0)
    query = db.session.query(host_guid.host_name, host_binary.execution_time, host_binary.md5hash, tg_binary.tg_id). \
            join(host_binary).join(tg_binary).join(host_ioc).join(tg_ioc).filter(tg_ioc.id==keyId)
    #print "\n", query, "\n"
    rows = [list(r) for r in query.all()]
    rows = process_date(rows, 1)
    return jsonify({'details':rows})

@app.route('/_get_host_details')
def get_host_details():
    keyId = request.args.get('keyId', 0)
    query = db.session.query(tg_ioc.title, host_binary.execution_time, tg_ioc.severity, tg_binary.tg_id). \
            join(host_ioc).join(host_binary).join(tg_binary).filter(host_binary.host_guid==keyId)
    print "\n", query, "\n", keyId
    rows = [list(r) for r in query.all()]
    rows = process_date(rows, 1)
    return jsonify({'details':rows})

@app.route('/_populate_iocs')
def populate_iocs():
    results = db.session.query(tg_ioc.unique_ioc_string).distinct().order_by(tg_ioc.unique_ioc_string)
    return jsonify({'iocs': [list(r) for r in results]})

@app.route('/_populate_hosts')
def populate_hosts():
    results = db.session.query(host_guid.host_name).distinct().order_by(host_guid.host_name).all()
    rows = [list(r) for r in results]
    return jsonify({'hosts': rows})

'''
Extracts unique categories from the string.
'''
def extract_categories(str):
    str = str.strip()
    if str != '':
        return str.split(',')
    return []

@app.route('/_populate_categories')
def populate_categories():
    results = db.session.query(tg_ioc.categories).distinct().all()
    cat = set([])
    for r in results:
        cat.update(extract_categories(r[0]))
    cat = sorted(cat)
    return jsonify({'categories':list(cat)})

@app.route('/_populate_severities')
def populate_severities():
    results = db.session.query(tg_ioc.severity).distinct().order_by(tg_ioc.severity).all()
    return jsonify({'severities': [list(r) for r in results]})

@app.route('/_populate_confidences')
def populate_confidences():
    results = db.session.query(tg_ioc.confidence).distinct().order_by(tg_ioc.confidence).all()
    return jsonify({'confidences': [list(r) for r in results]})

@app.route('/')
def hello():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

