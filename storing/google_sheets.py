# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 14:38:20 2020

@author: eerem
"""

from googleapi import google_sheets_rest_api as gshapi

google_api_service = gshapi.get_google_sheets_api_service()


def dump_feedback(df, context):
    spreadsheet_id = '1vRzwZFJ94Hfufk2yQPgFNPp8mlTLiaQt77GuDIq_GqQ'  # Cloud Function Uploading 29112019
    range_name = 'W1'

    values = df.to_json(orient='values', force_ascii=False)
    print(values)
    append_body = {'values': eval(values)}  # eval требуется здесь , так как df.json возвращает строку, которую
    # нужно интерпретировать как python код определения данного dict

    result = google_api_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=append_body).execute()
    print('{0} cells appended.'.format(result \
                                       .get('updates') \
                                       .get('updatedCells')))
