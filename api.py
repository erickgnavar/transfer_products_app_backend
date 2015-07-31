# coding: utf-8

import json
import xmlrpclib

from flask import Flask, Response, request

app = Flask(__name__)


def prepare_socket(host):
    return xmlrpclib.ServerProxy('{}/xmlrpc/object'.format(host))


def pool(model, host, dbname, uid, pwd):
    def wrapper(*args):
        return prepare_socket(host).execute(dbname, uid, pwd, model, *args)
    return wrapper


@app.route('/auth/login', methods=['POST'])
def login():
    params = json.loads(request.data)
    sock_common = xmlrpclib.ServerProxy('{}/xmlrpc/common'.format(params['host']))
    uid = sock_common.login(params['database'], params['email'], params['password'])
    response = Response(json.dumps({
        'status': 'ok',
        'credentials': '#'.join([params['host'], params['database'], str(uid), params['password']])
    }), mimetype='application/json', headers={
        'Access-Control-Allow-Origin': '*'
    })
    return response


@app.route('/api/products/')
def products():
    host, dbname, uid, password = request.headers['credentials'].split('#')
    db_products = pool('product.product', host, dbname, int(uid), password)
    data = []
    qs = []
    if request.args.get('q', ''):
        qs = [('name', 'ilike', request.args.get('q', ''))]
    elif request.args.get('code', ''):
        qs = [('default_code', '=', request.args.get('code', ''))]
    for product in db_products('read', db_products('search', qs), ['name', 'default_code']):
        data.append({
            'id': product['id'],
            'name': product['name'],
            'code': product['default_code']
        })
    response = Response(json.dumps(data), mimetype='application/json', headers={
        'Access-Control-Allow-Origin': '*'
    })
    return response


@app.route('/api/locations/')
def locations():
    host, dbname, uid, password = request.headers['credentials'].split('#')
    db_locations = pool('stock.location', host, dbname, int(uid), password)
    data = []
    for location in db_locations('read', db_locations('search', [
        ('name', 'ilike', request.args.get('q', ''))
    ]), ['name']):
        data.append({
            'id': location['id'],
            'name': location['name']
        })
    response = Response(json.dumps(data), mimetype='application/json', headers={
        'Access-Control-Allow-Origin': '*'
    })
    return response


@app.route('/api/locations/transfer/', methods=['POST'])
def transfer():
    params = json.loads(request.data)
    host, dbname, uid, password = request.headers['credentials'].split('#')
    db_transfer_product = pool('transfer.product.history', host, dbname, int(uid), password)
    res = db_transfer_product('make_transfer', params['product_id'], params['origin_id'], params['destination_id'])
    response = Response(json.dumps(res), mimetype='application/json', headers={
        'Access-Control-Allow-Origin': '*'
    })
    return response


@app.route('/api/history/')
def history():
    host, dbname, uid, password = request.headers['credentials'].split('#')
    db_transfer_product = pool('transfer.product.history', host, dbname, int(uid), password)
    data = []
    for _history in db_transfer_product('read', db_transfer_product('search', [
        ('user_id', '=', int(uid))
    ]), []):
        data.append({
            'product': {
                'name': _history['product_id'][1]
            },
            'origin': {
                'name': _history['origin_id'][1]
            },
            'destination': {
                'name': _history['destination_id'][1]
            }
        })
    response = Response(json.dumps(data), mimetype='application/json', headers={
        'Access-Control-Allow-Origin': '*'
    })
    return response

if __name__ == '__main__':
    app.run()
