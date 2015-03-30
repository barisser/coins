import db

def init():
    dbstring = "create table assets (name varchar(300), source_address varchar(400), asset_address varchar(400), metadata varchar(30));"
    db.dbexecute(dbstring, False)

    dbstring = "create table color_transfer_tx_queue (sender_public varchar(300), sender_private varchar(300), receiver_public varchar(300), fee bigint, asset_address varchar(300), color_amount bigint, success bool, txhash varchar(300), metadata varchar(30), randomid varchar(300));"
    db.dbexecute(dbstring, False)

    dbstring = "create table color_issue_tx_queue (sender_public varchar(300), sender_private varchar(300), receiver_public varchar(300), fee bigint, asset_address varchar(300), color_amount bigint, success bool, txhash varchar(300), metadata varchar(30), randomid varchar(300), name varchar(300));"
    db.dbexecute(dbstring, False)

    dbstring = "create table btc_tx_queue (sender_public varchar(300), sender_private varchar(300), receiver_public varchar(300), fee bigint, amount bigint, success bool, txhash varchar(300), randomid varchar(300));"
    db.dbexecute(dbstring, False)

def reset():
    dbstring = "drop table assets;drop table color_transfer_tx_queue;drop table color_issue_tx_queue;drop table btc_tx_queue;"
    db.dbexecute(dbstring, False)
    init()
