import requests
import json
import bitcoin
import os

def sign_tx(unsigned_raw_tx, privatekey):
  tx2=unsigned_raw_tx

  detx=bitcoin.deserialize(tx2)
  input_length=len(detx['ins'])

  for i in range(0,input_length):
    tx2=bitcoin.sign(tx2,i,privatekey)

  return tx2

def pushtx(rawtx):
  url="https://api.chain.com/v1/bitcoin/transactions"
  data = {}

  authstuff=(os.environ['CHAIN_API_KEY'], os.environ['CHAIN_API_KEY_SECRET'] )

  print "PUSHING RAW TX:"
  print rawtx
  print ''

  data['hex'] = rawtx
  jsondata=json.dumps(data)
  response=requests.post(url, data=jsondata, auth=authstuff)
  print "Push Response was "+str(response.content)
  jsonresponse=json.loads(response.content)
  if 'transaction_hash' in jsonresponse:
    return str(jsonresponse['transaction_hash'])
  else:
    return "None"

def push_tx_coinprism(rawtx):
    url = "https://api.coinprism.com/v1/sendrawtransaction"
    data = rawtx
    headers = {
        'Content-Type': 'application/json'
    }
    print data
    resp = requests.post(url, data = data, verify=False, headers = headers)
    return json.loads(resp.content)

def analyze_raw(rawtx):
    data = {}
    data['values'] = []
    data['values'].append(rawtx)
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps(data)
    url = "https://api.coinprism.com/v1/analyzerawtransactions"
    resp = requests.post(url, data=data, headers=headers, verify=False)
    return json.loads(resp.content)

def transfer_unsigned_raw(from_address, to_btc_address, amount, asset_id, fees):
    to_btc_address = convert_to_oa(to_btc_address)
    print "Open Assets format destination address BELOW"
    print to_btc_address
    #from_address = convert_to_oa(from_address)
    data = {}
    data['fees'] = int(fees)
    data['from'] = from_address
    data['to'] = []
    r = {}
    r['address'] = to_btc_address
    r['amount'] = int(amount)
    r['asset_id'] = asset_id
    data['to'].append(r)
    data = json.dumps(data)
    print "DATA SENT TO COINPRISM FOR RAW TX CREATION BELOW"
    print data

    url = "https://api.coinprism.com/v1/sendasset?format=raw"
    headers = {
        'Content-Type': 'application/json'
    }
    resp = requests.post(url, data=data, verify=False, headers = headers)

    return json.loads(resp.content), url, data, headers

def issue_asset_unsigned_raw(from_address, to_btc_address, amount, metadata, fees):
    data = {}
    to_oa_address = convert_to_oa(to_btc_address)
    data['fees'] = int(fees)
    data['from'] = from_address
    data['address'] = to_oa_address
    data['amount'] = amount
    data['metadata'] = metadata

    url = "https://api.coinprism.com/v1/issueasset?format=raw"
    resp = requests.post(url, data=data, verify=False)

    return json.loads(resp.content)

def issue_asset(from_address, to_btc_address, amount, metadata, fees, private_key):
    rawtx = issue_asset_unsigned_raw(from_address, to_btc_address, amount, metadata, fees)
    rawtx = str(rawtx['raw'])
    tx = sign_tx(rawtx, private_key)
    #resp = push_tx_coinprism(tx)
    resp = pushtx(tx)
    return resp

def transfer_asset(from_address, to_btc_address, amount, metadata, fees, private_key, asset_id):
    rawtx = transfer_unsigned_raw(from_address, to_btc_address, amount, asset_id, fees)
    print "RAW TX BELOW"
    print rawtx
    if len(rawtx)> 0:
        if 'raw' in rawtx[0]:
            rawtx = str(rawtx[0]['raw'])
            tx = sign_tx(rawtx, private_key)
            print tx
    #resp = push_tx_coinprism(tx)
            resp = pushtx(tx)
            return resp
    else:
        return 'Failed to transfer '+(from_address)+" "+str(to_btc_address)

def get_balance(address):
    url = "https://api.coinprism.com/v1/addresses/"+str(address)
    resp = requests.get(url, verify=False)
    return json.loads(resp.content)

def get_asset_id(address): #assumes only one asset type held
    a = get_balance(address)
    if len(a['assets'])>0:
        return a['assets'][0]['id']
    else:
        return -1

def convert_to_oa(address):
    return get_balance(address)['asset_address']
