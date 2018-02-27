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
    'localhost',
    'https://steemd.steemit.com',
]

FILTERED_OPERATIONS = ["vote","comment","transfer","transfer_to_vesting"]
BOT_AUTHOR_THRESHOLD = 5
BOT_VOTER_THRESHOLD = 5
BOT_TRANSFER_THRESHOLD = 5

def process_operation(db, operation):
    logging.info("Processing operation %s", operation['type'])

    if operation['type'] == "vote":
        if db.get(operation['voter'] + "_votes"):
            db.set(operation['voter'] + "_votes", db.get(operation['voter'] + "_votes") + 1)
        else:
            db.set(operation['voter'] + "_votes", 1)
    elif operation['type'] == "comment":
        if db.get(operation['author'] + "_comments"):
            db.set(operation['author'] + "_comments", db.get(operation['author'] + "_comments") + 1)
        else:
            db.set(operation['author'] + "_comments", 1)
    elif operation['type'] == "transfer":
        if db.get(operation['to'] + "_transfers"):
            db.set(operation['to'] + "_transfers", db.get(operation['to'] + "_transfers") + 1)
        else:
            db.set(operation['to'] + "_transfers", 1)
    elif operation['type'] == "transfer_to_vesting":
        if db.get(operation['to'] + "_vesting_transfers"):
            db.set(operation['to'] + "_vesting_transfers", db.get(operation['to'] + "_vesting_transfers") + 1)
        else:
            db.set(operation['to'] + "_vesting_transfers", 1)

def fill_storage(storage, chain, first_block, last_block):
    for operation in chain.history(start_block = first_block, end_block = last_block, filter_by = FILTERED_OPERATIONS):
        process_operation(storage, operation)

def main():
    db = pickledb.load('steem_analysis.db', False)

    steemd = Steem(STEEM_NODES)
    chain = Blockchain(steemd_instance = steemd, mode = 'head')

    logging.getLogger().setLevel(20)

    fill_storage(db, chain, round((1497970800 - 1451606400) / 3), chain.info()['head_block_number'])

    db.dump()

    analyze(db)


if __name__ == "__main__":
    main()
