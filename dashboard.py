from flask import render_template, request, jsonify
from models import app, tg_ioc, host_binary


@app.route('/_get_iocs')
def get_iocs():
    columns = ['id', 'title']
    return get_datatable_items(tg_ioc, columns)

@app.route('/_get_host_binaries')
def get_host_binaries():
    columns = ['id', 'host_guid']
    return get_datatable_items(host_binary, columns)

def get_datatable_items(table, columns):
    # sorting
    order = []
    sortingCols = int(request.args.get('iSortingCols', 0))
    for i in range(sortingCols):
        val = int(request.args.get('iSortCol_%d' % i, '0'))
        isSortable = request.args.get('bSortable_%d' % val, 'false')
        if isSortable == 'true':
            order.append(columns[val] + ' ' + request.args.get('sSortDir_%d' % i, 'desc'))

    # filtering TODO
    where = {}
    search = request.args.get('sSearch', '')
    if search != '':
        where[columns[1]] = search

    # record count before filtering
    count = table.query.count()

    start = int(request.args.get('iDisplayStart', 0))
    limit = int(request.args.get('iDisplayLength', 10))

    # main query with filter, order and paginate
    query = table.query.filter_by(**where)
    filtered_count = query.count()
    query = query.order_by(*order).limit(limit).offset(start)
    print query
    results = query.all()

    rows = []
    for r in results:
        vals = [getattr(r, sel) for sel in columns]
        rows.append(vals)
    d = {   'sEcho':request.args.get('sEcho',0),
            'iTotalRecords':count,
            'iTotalDisplayRecords':filtered_count,
            'aaData':rows}
    return jsonify(d)

@app.route('/')
def hello():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

