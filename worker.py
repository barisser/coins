import db
import coinprism
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
            db.dbexecute("update btc_tx_queue set txhash='"+str(txhash)+"' where randomid='"+str(randomid)+"';", False)

def issue_colors():

def transfer_colors():
