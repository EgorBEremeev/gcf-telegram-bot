# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 14:39:09 2020

@author: eerem
"""

import os

from google.cloud import firestore

PROJECT_ID = os.getenv('GCP_PROJECT')
# print('Get value of GCP_PROJECT: {}'.format(PROJECT_ID))

firedb = firestore.Client()


def dump_update(update, context):
    chat_id, message_id = context.chat_data['chat_id'], context.chat_data['message_id']

    # Adding the Update-object into the dedicated collection on the Google
    # Firestore service
    firedb.collection('chat_updates_from_' + chat_id).document(message_id).set(update.to_dict())
