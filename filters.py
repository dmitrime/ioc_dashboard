from models import tg_ioc, host_binary, host_guid
from sqlalchemy import or_
import datetime

def is_null(var):
    return var == '' or var == 'null'

def filter_date(query, exec_date, after):
    if exec_date:
        try:
            dt = datetime.datetime.strptime(exec_date, '%m/%d/%Y')
            if after:
                query = query.filter(host_binary.execution_time >= dt)
            else:
                query = query.filter(host_binary.execution_time <= (dt+datetime.timedelta(days=1))) # make this inclusive
        except ValueError:
            pass
    return query

def filter_hosts(query, hosts):
    if query == None or is_null(hosts):
        return None
    vals = [int(v) for v in hosts.split(',')]
    return query.filter(host_binary.host_guid.in_(vals))

def filter_iocs(query, iocs):
    if query == None or is_null(iocs):
        return None
    vals = [int(v) for v in iocs.split(',')]
    return query.filter(tg_ioc.id.in_(vals))

def filter_categories(query, categs):
    if query == None or is_null(categs):
        return None
    vals = [tg_ioc.categories.like('%'+cat+'%') for cat in categs.split(',')]
    return query.filter(or_(*vals))

def filter_severities(query, sevs):
    if query == None or is_null(sevs):
        return None
    vals = [int(v) for v in sevs.split(',')]
    return query.filter(tg_ioc.severity.in_(vals))

def filter_confidences(query, confs):
    if query == None or is_null(confs):
        return None
    vals = [int(v) for v in confs.split(',')]
    return query.filter(tg_ioc.confidence.in_(vals))

'''
Returns None when all checkboxes are unchecked for some filter,
otherwise the filtered query.
'''
def filter_all(query, exec_date, exec_date2, iocs, hosts, categs, sevs, confs):
    query = filter_date(query, exec_date, True)
    query = filter_date(query, exec_date2, False)
    query = filter_iocs(query, iocs)
    query = filter_hosts(query, hosts)
    query = filter_categories(query, categs)
    query = filter_severities(query, sevs)
    query = filter_confidences(query, confs)
    return query

