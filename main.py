# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 22:45:30 2019

@author: eerem
"""
import functools
import logging

from telegram import Update

from bot import bot_name

dispatcher = None


# def test_download(request):
#    cam.test()

# This fuction were added when GCF had problems with logging failed function's executions.
# Probably it is already fixed, however this option works in my currently deployed function
def catch_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.info(f"Uncaught exception, {e}", exc_info=e)

    return wrapper


@catch_exceptions
def hook_bot(request):
    """
    This function is a webhook function for Telegram BuhBot
    With the every new instance of Cloud Function Instance
    the Telegram Bot Dispatcher is initialized. And keep working while instance
    is not wasted (according configured to GCP policy)

    Also the TensorFlow Model is loaded and saved as Bot context attributes.

    Parameters
    ----------
    request : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    global dispatcher

    if dispatcher is None:
        print('There is no bot_dispatcher. Initializing one...')
        dispatcher = bot_name.init_bot_dispatcher()
        # Instead of global variable we can put google_api_service object into bot context,
        # this work starting from python-telegram-bot==12.4
        # dispatcher.bot_data = {'google_api_service': buhbot.init_google_api_service_in_context()}
    print('Bot dispatcher is instantiated as: ' + str(dispatcher))
    # print('google_api_service is instantiated as: ' + str(dispatcher.bot_data['fhfm_engine']))

    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), dispatcher.bot)
        dispatcher.process_update(update)
        print(update)

    # After migrating to python 3.9 runtime I started get this:
    # File "/layers/google.python.pip/pip/lib/python3.9/site-packages/flask/app.py", line 2097,
    # in make_response raise TypeError( TypeError: The view function did not return a valid response. The function
    # either returned None or ended without a return statement.
    #
    # So according to https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.make_response
    # I'm adding this
    return ('Ok', 200)
