import db
import coinprism
import time
import transactions

def worker_cycle():
    send_plain_btc()
    issue_colors()
    transfer_colors()

def send_plain_btc():
    txs = db.unsent_btc_transfers()
    for tx in txs:
        sender_public = tx[0]
        sender_private = tx[1]
        receiver_public = tx[2]
        fee = tx[3] #satoshi
        amount = tx[4] #satoshi
        randomid = tx[6]

        btc_value = amount*0.00000001
        txhash = send_btc(sender_public, sender_private, receiver_public, btc_value)
        if len(txhash)>10:
            db.dbexecute("update btc_tx_queue set txhash='"+str(txhash)+"', success=True where randomid='"+str(randomid)+"';", False)

def issue_colors():
    txs = db.unsent_issue_txs()
    for tx in txs:
        sender_public = tx[0]
        sender_private = tx[1]
        receiver_public = tx[2]
        fee = tx[3]
        asset_address = tx[4]
        color_amount = tx[5]
        metadata = tx[8]
        randomid = tx[9]

        r = coinprism.issue_asset(sender_public, receiver_public, color_amount, metadata, fees, sender_private)
        if len(r) > 10:
            txhash = r
            dbstring = "update color_issue_tx_queue set txhash='"+str(r)+"', success=True where randomid = '"+str(randomid)+"';"
            db.dbexecute(dbstring, False)

def transfer_colors():
    txs = db.unsent_transfer_txs()
    for tx in txs:
        sender_public = tx[0]
        sender_private = tx[1]
        receiver_public = tx[2]
        fee = tx[3]
        asset_address = tx[4]
        color_amount = tx[5]
        metadata = tx[8]
        randomid = tx[9]

        txhash = coinprism.transfer_asset(sender_public, receiver_public, color_amount, metadata, fee, sender_private, asset_address)
        if len(txhash) > 10:
            dbstring = "update color_transfer_tx_queue set txhash='"+str(txhash)+"', success=True where randomid='"+str(randomid)+"';"
            db.dbexecute(dbstring, False)


start=time.time()
interval=30
while True:
  if time.time()>=interval+start:
    start=time.time()
    worker_cycle()
