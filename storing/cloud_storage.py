# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 14:39:26 2020

@author: eerem
"""

import json
import os

from google.cloud import storage

PROJECT_ID = os.getenv('GCP_PROJECT')
print('Get value of GCP_PROJECT: {}'.format(PROJECT_ID))

BUCKET = os.environ['FHFM_TELEGRAM_BOT_BUCKET']
print('Get value of FHFM_TELEGRAM_BOT_BUCKET: {}'.format(BUCKET))

storage_client = storage.Client()
bucket = storage_client.get_bucket(BUCKET)

cloud_storage_chat_updates_dir = 'chat_updates/'
cloud_storage_operations_dir = 'operations/'


def dump_update(update, context):
    chat_id, message_id = context.chat_data['chat_id'], context.chat_data['message_id']

    # Uploading the Update-object as json file on a dedicated segment of
    # the Google Cloud Storage service
    bstr_data = json.dumps(update.to_dict(),
                           ensure_ascii=False).encode(
        encoding='utf-8')  # ensure encoding as default behavior of blob.upload_from_string() produce utf-8

    file_name = chat_id + '_' + message_id + '.json'
    destination_blob_name = cloud_storage_chat_updates_dir + file_name
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(bstr_data, content_type='application/json')
