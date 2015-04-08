import os
import psycopg2
import sys
import urlparse
import time

con=None

urlparse.uses_netloc.append('postgres')
url = urlparse.urlparse(os.environ['DATABASE_URL'])

def dbexecute(sqlcommand, receiveback):
  databasename=os.environ['DATABASE_URL']
  #username=''
  con=psycopg2.connect(
    database= url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
  )
  result=''
  cur=con.cursor()

  cur.execute(sqlcommand)
  if receiveback:
      result=cur.fetchall()

  con.commit()
  cur.close()
  con.close()
  return result

def unsent_btc_transfers():
    dbstring = "select * from btc_tx_queue where success='False';"
    a = dbexecute(dbstring, True)
    return a

def unsent_issue_txs():
    dbstring = "select * from color_issue_tx_queue where success='False';"
    a = dbexecute(dbstring, True)
    return a

def unsent_transfer_txs():
    dbstring = "select * from color_transfer_tx_queue where success='False';"
    a = dbexecute(dbstring, True)
    return a

def issued_without_asset_address():
    dbstring = "select * from color_issue_tx_queue where asset_address='' and success=True;"
    a = dbexecute(dbstring, True)
    return a

def assets_without_address():
    dbstring = "select * from assets where asset_address='' or asset_address='-1';"
    return dbexecute(dbstring, True)

def add_asset(name, source_address, asset_address, metadata):
    r = dbexecute("select count(*) from assets where name='"+str(name)+"';", True)
    if r[0][0]==0:
        dbstring = "insert into assets values ('"+str(name)+"', '"+str(source_address)+"', '"+str(asset_address)+"', '"+str(metadata)+"');"
        dbexecute(dbstring, False)

def update_asset_address_on_asset(name, source_address, asset_address):
    dbstring = "update assets set asset_address='"+str(asset_address)+"' where name='"+str(name)+"' and source_address='"+str(source_address)+"';"
    dbexecute(dbstring, False)

def btc_transactions_with_identifier(identifier):
    dbstring = "select * from btc_tx_queue where randomid='"+str(identifier)+"';"
    a = dbexecute(dbstring, True)
    b = []
    for x in a:
        b.append(x[6])
    return b

def color_transfer_transactions_with_identifier(identifier):
    dbstring = "select * from color_transfer_tx_queue where randomid='"+str(identifier)+"';"
    a = dbexecute(dbstring, True)
    b = []
    for x in a:
        b.append(x[7])
    return b

def color_issue_transactions_with_identifier(identifier):
    dbstring = "select * from color_issue_tx_queue where randomid='"+str(identifier)+"';"
    a = dbexecute(dbstring, True)
    b = []
    for x in a:
        b.append(x[7])
    return b

def backlog():
    btc = dbexecute("select count(*) from btc_tx_queue where success='false';", True)
    btc = btc[0][0]
    transfer = dbexecute("select count(*) from color_transfer_tx_queue where success='false';", True)
    transfer = transfer[0][0]
    issue = dbexecute("select count(*) from color_issue_tx_queue where success='false';", True)
    issue = issue[0][0]
    a = {}
    a['btc_transactions_backlog'] = btc
    a['color_transfer_backlog'] = transfer
    a['color_issue_backlog'] = issue
    return a
