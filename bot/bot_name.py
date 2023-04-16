#!/usr/bin/env python
# coding: utf-8

import base64
import json
import os

import pandas as pd

from google.cloud import pubsub_v1
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import Dispatcher

from googleapi import cloud_function_rest_api as cfapi
from storing import storing

ENGINE_HOST_CF_NAME = os.environ['ENGINE_HOST_CF_NAME']

google_api_service = None


def fhfm_engine_rest_api_call(event_context, payload):
    global google_api_service
    # Так сделано через global потому что, как я прочитал, при поднятии контейнера функции на холодном старте глобальные
    # переменные могут сохраниться и это ускорит холодный старт
    if google_api_service is None:
        google_api_service = cfapi.get_cloud_function_api_service()

    name = ENGINE_HOST_CF_NAME

    print(f'event_context: {event_context}')
    print(f'payload: {payload}')

    data = {'event_context': event_context,
            'payload': payload
            }
    body = {'data': json.dumps(data)}
    result = None
    try:
        result_call = google_api_service.projects().locations().functions().call(name=name, body=body).execute()
    except Exception as e:
        print('Обработка поступившего сообщения прервана с ошибкой: ',
              e.args)
    else:
        # print(engine_response)
        try:
            result = result_call['result']
        except KeyError as e:
            # отсутсвие ключа 'result' значит что пришел ключ 'error', в бот текст error отправлять смысла нет,
            # поэтому формирую константное сообщение об ошибке
            print('Обработка поступившего сообщения прервана с ошибкой: ',
                  result_call['error'])
        else:
            result = json.loads(result) # 'это будет dict

    return result # None или dict


def put_ids_into_context(update, context):
    context.chat_data['chat_id'] = str(update.effective_chat.id)
    context.chat_data['message_id'] = str(update._effective_message.message_id)
    context.user_data['user_id'] = str(update._effective_user.id)


# In[54]: Define message handlers
def process_message_type_1(update, context):
    # В этой версии, т.е. начиная с 03.12.2020 отказался от dumping приходящих updates в firestore и cloud storage,
    # также не загружаю raw updates в таблицу BigQuery
    # Такое решение обусловлено практической бесполезностью raw данных с updates на фоне распарсенной operation
    # из текста update, а трудоемкость с таблицей в BQ имеет место быть.
    put_ids_into_context(update, context)

    event_context = {
        "initiator": {
            "channel": "TELEGRAM_CHAT_BOT",
            "name": context.bot.username,
            "telegram_channel_context": {
                "user_id": context.user_data['user_id'],
                "message_id": context.chat_data['message_id'],
                "chat_id": context.chat_data['chat_id']
            },
            # "api_polling_context": {
            #     "interval_start": "2020-09-30T00:00:00.000Z",
            #     "interval_end": "2020-09-30T23:59:59.999Z"
            # }
        },
        "payload_metadata": {
            "type": "string",
            # "file_metadata": {
            #     "file_type": "csv txt pdf",
            #     "file_name": "file name"
            # },
            # "voice_metadata": {
            #     "codec": "wav",
            #     "file_name": "file name"
            # }
        }
    }

    payload = update.message.text

    # Далее идет собственно реализация обработки текста полученного текста.
    # У меня обработка реализована в отдельной CF, которая треггериться HTTP запросом по REST API
    # В вызываемой функции у меня логика применения модели классификатора, и поэтому имело смысл убрать много кода в
    # отдельную функцию. Но это оказалась не тревиальная интеграция двух CF по HTTP REST API, подробнее я написал на
    # Stackoverflow: https://stackoverflow.com/questions/42784000/calling-a-cloud-function-from-another-cloud-function/63959295#63959295
    # Или тут можно посмотреть и оценить нужно ли так.
    # Если делать по-простому, то с жтого места просто вставить код обработки `payload`
    engine_response = fhfm_engine_rest_api_call(event_context, payload)

    if engine_response:
        engine_response_payload = engine_response['payload_data']
        if engine_response_payload:
            # Вообще в респонсе для операции в сообщении мы ожидаем получить предсказанную иерархию счетов,
            # чтобы пользовать сразу дал фидбек: верно/не верно
            # Однако пайплайн может прерваться по какой-либо причине раньше, тогда payload_data вернется None
            # При нормальном завершении, ожидаем получить структуру данных list, в которой тем не менее могут быть
            # пустые строки для тех уровней иерархии, где значения не предусмотрены в Плане Счетов
            acctd_names_list = engine_response_payload
            # далее удаляем из списка пустые строки, т.е. не заполненные уровни иерархие счетов
            acctd_names_list = [item for item in acctd_names_list if item != '']
            # '' означает, что для данного уровня не определен счет в Плане Счетов.
            # Оставляем только описания для присутствующих уровней иерархии счетов.

            # Далее.
            # Строка сообщения имеет такой формат: наименование уровня + перенос строки + отступ (3 пробела)*(номер уровня -1)
            # Строки получаем перебором по списку столбцов, который берем из атрибута модели: m._acctd_joint_col_list
            # И соединяем их методом str.join() через разделитель '\'->'. Слэш здесь для экранирования одинарной кавычки
            # Учитываем то, что в конце получится лишние пробелы и перенос строки, удаляем их с помощью str.rstrip(' \n')

            acctd_formated_text = '\'->'.join(
                item + '\n' + ''.rjust(3 * (n + 1)) for n, item in enumerate(acctd_names_list)) \
                .rstrip(' \n')

            reply_text = 'Категория определена как: \n' + acctd_formated_text

            keyboard = [[InlineKeyboardButton("Верно", callback_data='Верно'),
                         InlineKeyboardButton("Не верно", callback_data='Не верно')]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            # sending the bot-replay message
            update.message.reply_text(reply_text,
                                      reply_markup=reply_markup,
                                      quote=True)
        else:
            reply_text = engine_response['pipeline_execution_status']
            update.message.reply_text(reply_text, quote=True)
    else:
        reply_text = 'FHFM-engine не смог обработать операцию из-за внутренней ошибки'
        update.message.reply_text(reply_text, quote=True)


def collect_feedback(update, context):
    """
    Тут все прямолинейно, обрабатываем сообщение типа CallbackQueryHandler, если в функции обработки основного
    сообщения отправляли кнопки
    :param update:
    :param context:
    :return:
    """
    query = update.callback_query

    fd = {'reply_to_message': str(query.message.reply_to_message.message_id),
          'feedback': query.data
          }
    feedback_df = pd.DataFrame([fd])  # As all values are scalar here we need make iterable from fd by [fd] to avoid
    # raising ValueError("If using all scalar values, you must pass an index")
    storing.dump_feedback(feedback_df, context)

    query.edit_message_text(text=query.message.text + ".\n\n Определено: {}".format(query.data))


def process_message_type_2(update, context):
    """
    Эта функция пример с обработчика для сообщений с файлом. Замечание про интеграцию с другой CF также применимы

    :param update:
    :param context:
    :return:
    """

    put_ids_into_context(update, context)
    filename = update.message.document.file_name
    context.chat_data['source_name'] = filename

    print('Message contains file with name: {}'.format(context.chat_data['source_name']))
    event_context = {
        "initiator": {
            "channel": "TELEGRAM_CHAT_BOT",
            "name": context.bot.username,
            "telegram_channel_context": {
                "user_id": context.user_data['user_id'],
                "message_id": context.chat_data['message_id'],
                "chat_id": context.chat_data['chat_id']
            },
            # "api_polling_context": {
            #     "interval_start": "2020-09-30T00:00:00.000Z",
            #     "interval_end": "2020-09-30T23:59:59.999Z"
            # }
        },
        "payload_metadata": {
            "type": "file",
            "file_metadata": {
                "file_type": filename.rsplit('.', 1)[-1],
                "file_name": filename
            },
            # "voice_metadata": {
            #     "codec": "wav",
            #     "file_name": "file name"
            # }
        }
    }

    file = update.message.document.get_file()
    print('File object: {}'.format(file))
    file_bytes = file.download_as_bytearray()
    # see https://stackoverflow.com/questions/53942948/encoding-and-decoding-binary-data-for-inclusion-into-json-with-python-3
    payload = base64.b64encode(file_bytes).decode('utf-8')

    engine_response = fhfm_engine_rest_api_call(event_context, payload)

    if engine_response:
        engine_response_payload = engine_response['payload_data']
        if engine_response_payload:
            reply_text = engine_response_payload
            update.message.reply_text(reply_text,
                                       quote=True)
        else:
            reply_text = engine_response['pipeline_execution_status']
            update.message.reply_text(reply_text, quote=True)
    else:
        reply_text = 'FHFM-engine не смог обработать операцию из-за внутренней ошибки'
        update.message.reply_text(reply_text, quote=True)


def command_1_callback(update, context):
    """
    Это обработчик для команды из бота, те которые через /command-name
    В этом обрботчике в Pub/Sub выклаждывается сообщение, которое треггирит реальную функцию обработчик. ОБратного
    ответа в бот здесь не отсылается, сообщение от телеграма обработано, когда в топик выложено сообщение

    :param update:
    :param context:
    :return:
    """
    publisher = pubsub_v1.PublisherClient()
    PROJECT_ID = os.getenv('GCP_PROJECT')
    TOPIC_NAME = os.environ['RETRAIN_TOPIC']
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
    try:
        # Пример команды в чате /retrain 3 12
        num_epochs = context.args[0]
        batch_size = context.args[1]
        data = 'hyper_parameters_custom'.encode('utf8')
        future = publisher.publish(topic_path, data=data, num_epochs=num_epochs, batch_size=batch_size)
    except (TypeError, IndexError) as e:
        data = 'hyper_parameters_defaults'.encode('utf8')
        future = publisher.publish(topic_path, data=data)

    print(future.result())
    reply_text = 'Задача на тренировку {} поставлена в очередь'.format(future.result())
    update.message.reply_text(reply_text)


# def error(update, context):
#    """Log Errors caused by Updates."""
#    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Init and run bot

def init_bot_dispatcher():

    TOKEN = 'your-token-here-or-read-it-from-secret-api'

    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), process_message_type_1))
    dispatcher.add_handler(MessageHandler(Filters.document, process_message_type_2))
    dispatcher.add_handler(CallbackQueryHandler(collect_feedback))
    dispatcher.add_handler(CommandHandler('retrain', command_1_callback))

    # log all errors
    # dispatcher.add_error_handler(error)

    return dispatcher
