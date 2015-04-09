from flask import *
import requests
import json
import transactions
import hashlib
import addresses
import coinprism
import db

app = Flask(__name__, static_url_path='/static')
app.config['PROPAGATE_EXCEPTIONS']=True

@app.route('/', methods=['GET'])
def home():
    return app.send_static_file('main.html')

@app.route('/quickstart', methods=['GET'])
def quickstart():
    return app.send_static_file('quickstart/index.html')

@app.route('/docs', methods=['GET'])
def api_docs():
    return app.send_static_file('docs/index.html')

@app.route('/whitepaper', methods=['GET'])
def whitepaper():
    return app.send_static_file('whitepaper/index.html')

@app.route('/backlog')
def showbacklog():
    a = db.backlog()
    responsejson=json.dumps(a)
    response=make_response(responsejson, 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin']= '*'
    return response

@app.route('/v2/colors/issue', methods=['POST'])   #WORKS
def givenewaddress_specifics():
    jsoninput=json.loads(request.data)

    public_address=str(jsoninput['public_address'])
    private_key=str(jsoninput['private_key'])

    coin_name=str(jsoninput['name'])
    color_amount=str(jsoninput['coins'])
    identifier = str(jsoninput['identifier'])
    dest_address=public_address

    #shortened = transactions.make_url_shortened(public_address, 8)
    metadata = str(jsoninput['metadata'])
    transactions.queue_issuing_tx(public_address, dest_address, private_key, metadata, color_amount, coin_name, identifier)
    tosend = transactions.default_fee * 0.00000001

    responsejson={}
    responsejson['message'] = "Issuing transaction queued.  Issuing address will send coins to itself.  Transfer from there."
    responsejson['required_btc'] = tosend + transactions.dust*0.00000001

    responsejson=json.dumps(responsejson)
    response=make_response(responsejson, 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin']= '*'
    return response

@app.route('/v2/identifiers/<identifier>')
def get_txhash(identifier=None):
    responsejson={}
    if identifier==None:
        k=0
    else:
        responsejson['btc_transfers'] = db.btc_transactions_with_identifier(identifier)
        responsejson['color_transfers'] = db.color_transfer_transactions_with_identifier(identifier)
        responsejson['color_issues'] = db.color_issue_transactions_with_identifier(identifier)
    responsejson=json.dumps(responsejson)
    response=make_response(responsejson, 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin']= '*'
    return response

@app.route('/v2/coinholders/<asset_address>')
def get_coinholders(asset_address=None):
    responsejson = {}
    responsejson['coinholders'] = coinprism.get_address_holding_asset_address(asset_address)
    responsejson=json.dumps(responsejson)
    response=make_response(responsejson, 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin']= '*'
    return response

@app.route('/v2/colors/transfer', methods=['POST'])
def transfer():
    jsoninput=json.loads(request.data)
    sender_public = str(jsoninput['public_address'])
    sender_private = str(jsoninput['private_key'])
    recipient_public = str(jsoninput['recipient_address'])
    amount = str(jsoninput['amount'])
    metadata = ""
    asset_address = str(jsoninput['asset_address'])
    identifier = str(jsoninput['identifier'])

    transactions.queue_transfer_tx(sender_public, sender_private, recipient_public, amount, metadata, asset_address, identifier)

    responsejson={}
    responsejson['message'] = "Color Transaction Queued"

    responsejson=json.dumps(responsejson)
    response=make_response(responsejson, 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin']= '*'
    return response

@app.route('/v2/btc/transfer', methods = ['POST'])
def send_btc():
    jsoninput = json.loads(request.data)
    sender_public = str(jsoninput['public_address'])
    sender_private = str(jsoninput['private_key'])
    recipient_public = str(jsoninput['recipient_address'])
    amount = str(jsoninput['amount'])
    identifier = str(jsoninput['identifier'])
    print str(sender_public)+"  "+str(sender_private)+"  "+str(recipient_public)+"   "+str(amount)
    transactions.queue_btc_tx(sender_public, sender_private, recipient_public, amount, identifier)

    responsejson={}
    responsejson['message'] = "BTC Transaction Queued"

    responsejson=json.dumps(responsejson)
    response=make_response(responsejson, 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin']= '*'
    return response

@app.route('/v2/addresses/')
def new_address():
    responsejson={}
    a = addresses.random_address_pair()
    responsejson['private_key'] = a[0]
    responsejson['public_key'] = a[1]
    responsejson['public_address'] = a[2]
    responsejson=json.dumps(responsejson)
    response=make_response(responsejson, 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin']= '*'
    return response

@app.route('/v2/colors/asset_address/<btc_address>')
def get_asset_address(btc_address=None):
    a = coinprism.get_asset_id(btc_address)
    responsejson = {}
    responsejson['asset_address'] = a
    responsejson=json.dumps(responsejson)
    response=make_response(responsejson, 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin']= '*'
    return response

@app.route('/last_txs')
def last_txs():
    n = 100
    a = db.get_last_transactions(n)
    responsejson = {}
    responsejson['last_txs'] = a
    responsejson=json.dumps(responsejson)
    response=make_response(responsejson, 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin']= '*'
    return response

if __name__ == '__main__':
    app.run()
