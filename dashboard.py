from flask import render_template, request, jsonify
from models import app, db, tg_ioc, host_binary, host_ioc
from sqlalchemy import func

@app.route('/_get_iocs')
def get_iocs():
    order = 'sum ' + request.args.get('sSortDir_0', 'desc')
    sum_by = request.args.get('sSumBy', 'severity')

    if sum_by == 'host_count':
        query = db.session.query(tg_ioc.title, func.count(host_binary.host_guid).label('sum')). \
                join(host_ioc).join(host_binary).group_by(tg_ioc.id).order_by(order)
    elif sum_by == 'severity':
        query = db.session.query(tg_ioc.title, tg_ioc.severity.label('sum')). \
                join(host_ioc).join(host_binary).group_by(tg_ioc.id).order_by(order)
    return get_datatable_items(query)

@app.route('/_get_host_binaries')
def get_host_binaries():
    order = 'sum ' + request.args.get('sSortDir_0', 'desc')
    sum_by = request.args.get('sSumBy', 'severity')

    if sum_by == 'ioc_count':
        query = db.session.query(host_binary.host_guid, func.count(tg_ioc.id).label('sum')). \
                join(host_ioc).join(tg_ioc).group_by(host_binary.host_guid).order_by(order)
    elif sum_by == 'severity':
        query = db.session.query(host_binary.host_guid, func.sum(tg_ioc.severity).label('sum')). \
                join(host_ioc).join(tg_ioc).group_by(host_binary.host_guid).order_by(order)
    return get_datatable_items(query)

def get_datatable_items(query):
    # filtering TODO
    #search = request.args.get('sSearch', '')

    # record count before filtering
    count = query.count()

    start = int(request.args.get('iDisplayStart', 0))
    limit = int(request.args.get('iDisplayLength', 10))

    print query
    results = query.limit(limit).offset(start).all()

    rows = [list(r) for r in results]
    d = {   'sEcho':request.args.get('sEcho',0),
            'iTotalRecords':count,
            #'iTotalDisplayRecords':filtered_count,
            'iTotalDisplayRecords':count,
            'aaData':rows}
    return jsonify(d)

@app.route('/_populate_iocs')
def populate_iocs():
    results = tg_ioc.query.order_by(tg_ioc.id).values(tg_ioc.title, tg_ioc.id)
    return jsonify({'iocs': [list(r) for r in results]})

@app.route('/_populate_hosts')
def populate_hosts():
    results = host_binary.query.group_by(host_binary.host_guid).values(host_binary.host_guid)
    return jsonify({'hosts': [list(r) for r in results]})

@app.route('/_populate_categories')
def populate_categories():
    results = tg_ioc.query.group_by(tg_ioc.categories).values(tg_ioc.categories)
    cat = set([])
    for r in results:
        cat.update(r[0].split(','))
    return jsonify({'categories':list(cat)})

@app.route('/')
def hello():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

