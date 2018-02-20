#!/usr/bin/env python
import json
import logging
import os
import re
import sys
import time

from contextlib import suppress

from steem.account import Account
from steem.blockchain import Blockchain
from steem.post import Post
from steembase.exceptions import PostDoesNotExist

MIN_NOTIFY_REPUTATION = 40

NTYPES = {
    'total': 0,
    'feed': 1,
    'reward': 2,
    'send': 3,
    'mention': 4,
    'follow': 5,
    'vote': 6,
    'comment_reply': 7,
    'post_reply': 8,
    'account_update': 9,
    'message': 10,
    'receive': 11
}

FILTERED_OPERATIONS = ["account_create","vote","comment","transfer","transfer_to_vesting"]
BOT_AUTHOR_THRESHOLD = 5
BOT_VOTER_THRESHOLD = 5
BOT_TRANSFER_THRESHOLD = 5

# gloabal variables
chain = None

accounts = [("initminer", 0, 0)]
bot_authors = []
bot_voters = []

processed_posts = {}

def process_operation(operation):
    global accounts
    global bot_authors
    global bot_voters

    logging.info("Processing operation %s", operation['type'])

    if operation['type'] == "account_create":
        accounts.append(tuple((operation['new_account_name'], 0, 0)))
    elif operation['type'] == "vote":
        exists = False
        for key in accounts:
            account, vote_amount, comment_amount = key
            if account == operation['voter']:
                exists = True

        if not exists:
            accounts.append(tuple((operation['voter'], 0, 0)))

        for key in accounts:
            account, vote_amount, comment_amount = key
            if operation['voter'] == account:
                if vote_amount > BOT_VOTER_THRESHOLD & comment_amount < BOT_AUTHOR_THRESHOLD:
                    bot_voters.append(account)
                    logging.info("Bot voter %s", account)
                elif vote_amount < BOT_VOTER_THRESHOLD & comment_amount > BOT_AUTHOR_THRESHOLD:
                    bot_authots.append(account)
                    logging.info("Bot author %s", account)

def analyze(first_block, last_block):
    for operation in chain.history(start_block = first_block, end_block = last_block, filter_by = FILTERED_OPERATIONS):
        process_operation(operation)

def main():
    global chain

    chain = Blockchain(mode = 'head')

    logging.getLogger().setLevel(20)

    analyze(round((1497970800 - 1451606400) / 3), chain.info()['head_block_number'])

if __name__ == "__main__":
    main()
