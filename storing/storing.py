# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 20:18:48 2019

@author: eerem
"""

# from storing import cloud_firestore as fs
# from storing import cloud_storage as cs
from storing import google_sheets as gsh


# def dump_update(update, context):
#     # Uploading the Update-object as json file on a dedicated segment of
#     # the Google Cloud Storage service
#     cs.dump_update(update, context)
#
#     # Adding the Update-object into the dedicated collection on the Google
#     # Firestore service
#     fs.dump_update(update, context)


def dump_feedback(df, context):
    gsh.dump_feedback(df, context)
