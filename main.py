from flask import *
import requests
import json
import transactions
import hashlib

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS']=True

@app.route('/', methods=['GET'])
def home():
    responsejson = {}
    responsejson['message']="AssemblyCoins V2"

    responsejson=json.dumps(responsejson)
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
    dest_address=public_address

    #shortened = transactions.make_url_shortened(public_address, 8)
    metadata = ""#"https://coins.assembly.com/colors/"+str(shortened)
    transactions.queue_issuing_tx(public_address, dest_address, private_key, metadata, color_amount)
    tosend = transactions.default_fee * 0.00000001

    responsejson={}
    responsejson['name']=coin_name
    responsejson['minting_fee']=tosend
    responsejson['issuing_public_address']=public_address
    responsejson['issuing_private_key']=private_key

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

    transactions.queue_transfer_tx(sender_public, sender_private, recipient_public, amount, metadata, asset_address)

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

    transactions.queue_btc_tx(sender_public, sender_private, recipient_public, amount)

    responsejson={}
    responsejson['message'] = "BTC Transaction Queued"

    responsejson=json.dumps(responsejson)
    response=make_response(responsejson, 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin']= '*'
    return response


if __name__ == '__main__':
    app.run()
