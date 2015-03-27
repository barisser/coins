#import db
import hashlib
import os
import bitcoin
import json
import requests
import coinprism

default_fee = 5000

def queue_issuing_tx(source_address, recipient_address, source_private, metadata, amount):
    dbstring = "insert into color_issue_tx_queue values ('"+str(source_address)+"', '"+str(source_private)+"', '"+str(recipient_address)+"', "+str(default_fee)+", '', "+str(amount)+", False, '"+str(metadata)+"');"
    db.dbexecute(dbstring, False)

def queue_transfer_tx(sender_public, sender_private, recipient_public, amount, metadata, asset_address):
    dbstring = "insert into color_transfer_tx_queue values ('"+str(sender_public)+"', '"+str(sender_private)+"', '"+str(recipient_public)+"', "+str(default_fee)+", '"+str(asset_address)+"', "+str(amount)+", False, '"+str(metadata)+"');"
    db.dbexecute(dbstring, False)

def queue_btc_tx(sender_public, sender_private, recipient_public, amount):
    amount = amount * 100000000
    dbstring = "insert into btc_tx_queue values ('"+str(sender_public)+"', '"+str(sender_private)+"', '"+str(recipient_public)+"', "+str(default_fee)+", "+str(amount)+", False,'');"
    db.dbexecute(dbstring, False)

def make_url_shortened(sender_public, length):
    return str(hashlib.sha256(sender_public).hexdigest())[0:length]

def send_btc_chain(from_addr, destination_address, btc_value):
    btc_value = btc_value * 100000000
    data = {}
    data['inputs'] = [{'address': from_addr}]
    data['outputs'] = [{'address': destination_address, 'amount': btc_value}]
    data['miner_fee_rate'] = default_fee
    d = json.dumps(data)
    print d
    authstuff=(os.environ['CHAIN_API_KEY'], os.environ['CHAIN_API_KEY_SECRET'] )
    url = "https://api.chain.com/v2/bitcoin/transactions/build"
    r = requests.post(url, data=d, auth=authstuff)
    return str(json.loads(r.content)['unsigned_hex'])

def send_btc(from_addr, private_key, destination_address, btc_value):
    a = send_btc_chain(from_addr, destination_address, btc_value)
    b = coinprism.sign_tx(a, private_key)
    coinprism.pushtx(b)
