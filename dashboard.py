from flask import Flask, render_template, request, jsonify
from flaskext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/tgstore.sdb'
db = SQLAlchemy(app)

class host_binary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host_guid = db.Column(db.Numeric)
    md5hash = db.Column(db.Text)
    execution_time = db.Column(db.DateTime)

    def __repr__(self):
        return "host_binary: <%d>" % self.id

class tg_ioc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_ioc_string = db.Column(db.Text, unique=True)
    categories = db.Column(db.Text)
    title = db.Column(db.Text)
    long_description = db.Column(db.Text)
    severity = db.Column(db.Integer)
    confidence = db.Column(db.Integer)

    def __repr__(self):
        return "tg_ioc: <%d>" % self.id


@app.route('/_get_iocs')
def get_iocs():
    columns = ['id', 'title']
    return get_datatable_items(tg_ioc, columns)

@app.route('/_get_host_binaries')
def get_host_binaries():
    columns = ['id', 'md5hash']
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

    print where
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

