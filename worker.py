import db
import coinprism
import time
import transactions

def worker_cycle():
    print "BEGINNING WORK CYCLE"
    send_plain_btc()
    issue_colors()
    transfer_colors()
    scrape_asset_addresses()

def send_plain_btc():
    txs = db.unsent_btc_transfers()
    for tx in txs:
        sender_public = tx[0]
        sender_private = tx[1]
        receiver_public = tx[2]
        fee = tx[3] #satoshi
        amount = tx[4] #satoshi
        randomid = tx[7]

        btc_value = amount*0.00000001
        try:
            txhash = transactions.send_btc(sender_public, sender_private, receiver_public, btc_value)
            print "TXHASH"
            print txhash
        except:
            print "ERROR MAKING TX"
            txhash = 'fail'

        if len(txhash)>10:
            dbstring = "update btc_tx_queue set txhash='"+str(txhash)+"', success=True where randomid='"+str(randomid)+"';"
            db.dbexecute(dbstring, False)
            db.add_to_last_transactions(txhash)

def issue_colors():
    txs = db.unsent_issue_txs()
    for tx in txs:
        sender_public = tx[0]
        sender_private = tx[1]
        receiver_public = tx[2]
        fees = tx[3]
        asset_address = tx[4]
        color_amount = tx[5]
        metadata = tx[8]
        randomid = tx[9]
        name = tx[10]

        r = coinprism.issue_asset(sender_public, receiver_public, color_amount, metadata, fees, sender_private)
        if len(r) > 10:
            txhash = r
            dbstring = "update color_issue_tx_queue set txhash='"+str(r)+"', success=True where randomid = '"+str(randomid)+"';"
            db.dbexecute(dbstring, False)
            db.add_to_last_transactions(txhash)
            db.add_asset(name, sender_public, '', metadata)


def transfer_colors():
    txs = db.unsent_transfer_txs()
    for tx in txs:
        sender_public = tx[0]
        sender_private = tx[1]
        receiver_public = tx[2]
        fee = tx[3]
        asset_address = tx[4]
        if len(str(asset_address))<10:
            asset_address = coinprism.get_asset_id(sender_public)
        color_amount = tx[5]
        metadata = tx[8]
        randomid = tx[9]

        if len(str(asset_address)) > 10:
            txhash = coinprism.transfer_asset(sender_public, receiver_public, color_amount, metadata, fee, sender_private, asset_address)
            try:
                if len(txhash) > 10:
                    dbstring = "update color_transfer_tx_queue set txhash='"+str(txhash)+"', success=True where randomid='"+str(randomid)+"';"
                    db.dbexecute(dbstring, False)
                    db.add_to_last_transactions(txhash)
            except:
                print "No tx"
        else:
            print "DONT HAVE ASSET ADDRESS FOR RANDOMID="+str(randomid)

def scrape_asset_addresses():
    addrs = db.assets_without_address()
    for addr in addrs:
        address = addr[1]
        name = addr[0]
        asset_address = coinprism.get_asset_id(address)
        if asset_address == -1:
            k=0
        else:
            db.update_asset_address_on_asset(name, address, asset_address)

def transfer_txs_without_asset_address():
    dbstring = "select * from color_transfer_tx_queue where success=false and asset_address='' or asset_address='-1';"
    a = db.dbexecute(dbstring, True)
    for tx in a:
        sender = tx[0]
        print tx
        asset_address = tx[4]
        randomid = tx[9]
        if len(asset_address) < 10:
            new_asset_address = coinprism.get_asset_id(sender)
            if new_asset_address == -1:
                k = 0
            elif len(new_asset_address)< 10:
                k = 0
            else:
                dbstring = "update color_transfer_tx_queue set asset_address='"+str(new_asset_address)+"' where randomid='"+str(randomid)+"'';"
                db.dbexecute(dbstring, False)

def process_btc_maintenances():
    open_maintenances = transactions.get_open_btc_maintenance()

    for m in open_maintenances:
        sender_public = m[0]
        sender_private = m[1]
        receiver_public = m[2]
        fee = m[3]
        amount = m[4]  #IN SATOSHIS
        last_sent = m[7]
        randomid = m[6]

        time_diff = time.time() - float(last_sent)
        if time_diff > 1000:
            current_balance = coinprism.check_btc_balance(receiver_public)
            if amount > current_balance+0.00001:  #send funds
                db.dbexecute("update btc_maintenance set last_sent="+str(int(time.time()))+" where randomid='"+str(randomid)+"';", False)

                print "MAINTAINING BTC BALANCE OF "+str(amount)+" FOR "+str(receiver_public)
                #clear pre-existing btc queued transactions for this receiving address to prevent double-sends
                transactions.clear_btc_tx_on_address(receiver_public)

                #queue a new tx
                identifier = str(int(time.time()))+"queue btc transfer to maintain "+str(receiver_public)
                transactions.queue_btc_tx(sender_public, sender_private, receiver_public, float(amount)/100000000, identifier)
