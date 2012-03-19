from flask import Flask, render_template, request, jsonify
from flask import g
import sqlite3
from math import ceil

app = Flask(__name__)

DATABASE = 'db/tgstore.sdb'

def connect_db():
    return sqlite3.connect(DATABASE)

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value) 
        for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def hello():
    #for ioc in query_db('select * from tg_ioc'):
    #    print ioc['title'], 'has the id', ioc['id']
    return render_template('index.html')

@app.route('/_get_iocs')
def get_iocs():
    columns = ['id', 'title']

    start = int(request.args.get('iDisplayStart', 1))
    limit = int(request.args.get('iDisplayLength', 10))

    # record count
    count = int(query_db('select count(id) as c from tg_ioc')[0]['c'])

    # sorting
    order = ' order by  '
    sortingCols = int(request.args.get('iSortingCols', 0))
    for i in range(sortingCols):
        val = int(request.args.get('iSortCol_%d' % i, '0'))
        isSortable = request.args.get('bSortable_%d' % val, 'false')
        if isSortable == 'true':
            order = order + columns[val] + ' ' + request.args.get('sSortDir_%d' % i, 'desc') + ', '
    order = order[:len(order) - 2] # remove last ', '
    if order == 'order by':
        order = ''

    # filtering
    where = ''
    search = request.args.get('sSearch', '')
    if search != '':
        where = " where title like '%" + search + "%' "

    # main query
    query = 'select ' + ", ".join(columns) + ' from tg_ioc '+ where + order + ' limit %d, %d' % (start, limit)
    print query
    results = query_db(query)
    rows = []
    for r in results:
        vals = [r[sel] for sel in columns]
        rows.append(vals)
    d = {   'sEcho':int(request.args.get('sEcho',0)),
            'iTotalRecords':count,
            'iTotalDisplayRecords':len(results),
            'aaData':rows}
    #print d
    return jsonify(d)


if __name__ == '__main__':
    app.run(debug=True)

