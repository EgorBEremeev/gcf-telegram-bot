# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 14:38:20 2020

@author: eerem
"""

# TODO: переписать код на сохранение файлов выписок на google disk
#  из текущего пригодится обращение к google api
# def get_google_api_service():
#
#     class MemoryCache(Cache):
#         _CACHE = {}
#
#         def get(self, url):
#             return MemoryCache._CACHE.get(url)
#
#         def set(self, url, content):
#             MemoryCache._CACHE[url] = content
#
#     scopes = ["https://www.googleapis.com/auth/spreadsheets",
#               "https://www.googleapis.com/auth/drive.file"] #TODO: mayby add dumping attached file into the current google drive folder
#     credentials, project_id = google.auth.default(scopes)
#     service = build('sheets', 'v4', credentials = credentials, cache = MemoryCache())
#     return service
#
# PROJECT_ID = os.getenv('GCP_PROJECT')
# print('Get value of GCP_PROJECT: {}'.format(PROJECT_ID))
#
#
# google_api_service = get_google_api_service()
#
# def dump_operation(df, context):
#     # Add the operation's data to the Google Data Sheet file
#
#     spreadsheet_id = '1vRzwZFJ94Hfufk2yQPgFNPp8mlTLiaQt77GuDIq_GqQ' #Cloud Function Uploading 29112019
#     range_name = 'A1'
#
#     values = df.to_json(orient='values', force_ascii=False)
#     append_body = {'values': eval(values)} #eval требуетсяздесь , так как df.json возвращает строку, которую нужно интерпретировать как python код определения данного dict
#
#     result = google_api_service.spreadsheets().values().append(
#                                                spreadsheetId=spreadsheet_id,
#                                                range=range_name,
#                                                valueInputOption='RAW',
#                                                body=append_body).execute()
#     print('{0} cells appended.'.format(result \
#                                        .get('updates') \
#                                        .get('updatedCells')))
#
# def dump_feedback(df, context):
#     spreadsheet_id = '1vRzwZFJ94Hfufk2yQPgFNPp8mlTLiaQt77GuDIq_GqQ' #Cloud Function Uploading 29112019
#     range_name = 'V1'
#
#     values = df.to_json(orient='values', force_ascii=False)
#     print(values)
#     append_body = {'values': eval(values)} #eval требуется здесь , так как df.json возвращает строку, которую нужно интерпретировать как python код определения данного dict
#
#     result = google_api_service.spreadsheets().values().append(
#                                                spreadsheetId=spreadsheet_id,
#                                                range=range_name,
#                                                valueInputOption='RAW',
#                                                body=append_body).execute()
#     print('{0} cells appended.'.format(result \
#                                        .get('updates') \
#                                        .get('updatedCells')))
#
#
# def dump_processed_statement(df):
#     # Add the operation's data from the statement to the Google Data Sheet file
#
#     spreadsheet_id = '1s-eHnM60_EJ2JCTdOzTutOFe_D6Pp6jL-E1KIiSd56w' #Bank_Statements_from_December_2019
#     range_name = 'A1'
#
#     values = df.to_json(orient='values', force_ascii=False)
#     append_body = {'values': eval(values)} #eval требуется здесь, так как df.json возвращает строку, которую нужно интерпретировать как python код определения данного dict
#
#     result = google_api_service.spreadsheets().values().append(
#                                                spreadsheetId=spreadsheet_id,
#                                                range=range_name,
#                                                valueInputOption='RAW',
#                                                body=append_body).execute()
#     print('{0} cells appended.'.format(result \
#                                        .get('updates') \
#                                        .get('updatedCells')))
