#!/usr/bin/env python
import json
import logging
import os
import re
import sys
import time

import pickledb

from contextlib import suppress

from steem import Steem
from steem.account import Account
from steem.blockchain import Blockchain
from steem.post import Post
from steembase.exceptions import PostDoesNotExist

STEEM_NODES = [
#    'localhost',
]

FILTERED_OPERATIONS = ["vote","comment","transfer","transfer_to_vesting"]
BOT_AUTHOR_THRESHOLD = 5
BOT_VOTER_THRESHOLD = 5
BOT_TRANSFER_THRESHOLD = 5

def process_operation(db, operation):
    logging.info("Processing operation %s", operation['type'])

    if operation['type'] == "vote":
        if db.get(operation['voter']):
            db.set(operation['voter'], db.get(operation['voter']) + 1)
        else:
            db.set(operation['voter'], 1)
    elif operation['type'] == "comment":
        if db.get(operation['author']):
            db.set(operation['author'], db.get(operation['author']) + 1)
        else:
            db.set(operation['author'], 1)
    elif operation['type'] == "transfer":
        if db.get(operation['to']):
            db.set(operation['to'], db.get(operation['to']) + 1)
        else:
            db.set(operation['to'], 1)
    elif operation['type'] == "transfer_to_vesting":
        if db.get(operation['to']):
            db.set(operation['to'], db.get(operation['to']) + 1)
        else:
            db.set(operation['to'], 1)

def fill(databases, chain, first_block, last_block):
    for operation in chain.history(start_block = first_block, end_block = last_block, filter_by = FILTERED_OPERATIONS):
        process_operation(databases[operation['type']], operation)

def main():
    votes_db = pickledb.load('steem_account_votes.db', False)
    comments_db = pickledb.load('steem_account_comments.db', False)
    transfers_db = pickledb.load('steem_account_trasnfers.db', False)
    vesting_transfers_db = pickledb.load('steem_account_vesting_transfers.db', False)

    steemd = Steem(STEEM_NODES)
    chain = Blockchain(steemd_instance = steemd, mode = 'head')

    logging.getLogger().setLevel(20)

    databases = {'vote': votes_db, 'comment': comments_db, 'transfer': transfers_db, 'transfer_to_vesting': vesting_transfers_db}

    fill(databases, chain, round((1497970800 - 1451606400) / 3), chain.info()['head_block_number'])

    votes_db.dump()
    comments_db.dump()
    transfers_db.dump()
    vesting_transfers_db.dump()


if __name__ == "__main__":
    main()
