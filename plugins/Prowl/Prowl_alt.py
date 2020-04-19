#!/usr/bin/python
# -- coding: UTF-8 --

"""
template plugin to show the function and usage of plugins
feel free to edit to yout own plugin
please edit theese desciption, the @author-Tag and the @requires-Tag
For more information take a look into the other plugins

@author: Jens Herrmann
@author: Bastian Schroll

@requires: none
"""
import logging  # Global logger
import httplib  # for the HTTP request
import urllib

#
# Imports
#
import logging  # Global logger
from includes import globalVars  # Global variables

# Helper function, uncomment to use
#from includes.helper import timeHandler
from includes.helper import wildcardHandler
from includes.helper import configHandler

##
#
# onLoad (init) function of plugin
# will be called one time by the pluginLoader on start
#


def onLoad():
    """
    While loading the plugins by pluginLoader.loadPlugins()
    this onLoad() routine is called one time for initialize the plugin

    @requires:  nothing

    @return:    nothing
    @exception: Exception if init has an fatal error so that the plugin couldn't work

    """
    try:
        ########## User onLoad CODE ##########
        pass
        ########## User onLoad CODE ##########
    except:
        logging.error("unknown error")
        logging.debug("unknown error", exc_info=True)
        raise

##
#
# Main function of Prowl
# will be called by the alarmHandler
#


def run(typ, freq, data):
    """
    This function is the implementation of the Pushover-Plugin.
    It will send the data to Pushover API

    @type    typ:  string (FMS|ZVEI|POC)
    @param   typ:  Typ of the dataset
    @type    data: map of data (structure see readme.md in plugin folder)
    @param   data: Contains the parameter
    @type    freq: string
    @keyword freq: frequency of the SDR Stick

    @requires:  Pushover-Configuration has to be set in the config.ini

    @return:    nothing
    """

    try:
        if configHandler.checkConfig("Prowl"):  # read and debug the config
            if typ == "FMS":
                #
                # building message for FMS
                #

                message = globalVars.config.get("Prowl", "fms_message")
                title = globalVars.config.get("Prowl", "fms_title")
                priority = globalVars.config.get("Prowl", "fms_prio")
                logging.debug("Sending message: %s", message)

            elif typ == "POC":

                #
                # Pushover-Request
                #
                if globalVars.config.get("Prowl", "poc_spec_ric") == '0':
                    if data["function"] == '1':
                        priority = globalVars.config.get("Prowl", "SubA")
                    elif data["function"] == '2':
                        priority = globalVars.config.get("Prowl", "SubB")
                    elif data["function"] == '3':
                        priority = globalVars.config.get("Prowl", "SubC")
                    elif data["function"] == '4':
                        priority = globalVars.config.get("Prowl", "SubD")
                    else:
                        priority = 0
                else:
                    if data["ric"] in globalVars.config.get("Prowl", "poc_prio2"):
                        priority = 2
                    elif data["ric"] in globalVars.config.get("Prowl", "poc_prio1"):
                        priority = 1
                    elif data["ric"] in globalVars.config.get("Prowl", "poc_prio0"):
                        priority = 0
                    else:
                        priority = -1

                message = globalVars.config.get("Prowl", "poc_message")
                title = globalVars.config.get("Prowl", "poc_title")

            else:
                logging.warning("Invalid type: %s", typ)

            try:
                # replace the wildcards
                message = wildcardHandler.replaceWildcards(message, data)
                title = wildcardHandler.replaceWildcards(title, data)

                # start the connection
                conn = httplib.HTTPSConnection("api.prowlapp.com/publicapi/add:443")
                conn.request("POST", "/1/messages.json",
                             urllib.urlencode({
                                 "token": globalVars.config.get("Prowl", "api_key"),
                                 "user": globalVars.config.get("Prowl", "user_key"),
                                 "message": message,
                                 "html": globalVars.config.get("Prowl", "html"),
                                 "title": title,
                                 "priority": priority,
                                 "retry": globalVars.config.get("Prowl", "retry"),
                                 "expire": globalVars.config.get("Prowl", "expire")
                             }), {"Content-type": "application/x-www-form-urlencoded"})

            except:
                logging.error("cannot send Prowl request")
                logging.debug("cannot send Prowl request", exc_info=True)
                return

            try:
                #
                # check Pushover-Response
                #
                response = conn.getresponse()
                if str(response.status) == "200":  # Check Pushover Response and print a Log or Error
                    logging.debug("Prowl response: %s - %s",
                                  str(response.status), str(response.reason))
                else:
                    logging.warning("Prowl response: %s - %s",
                                    str(response.status), str(response.reason))
            except:  # otherwise
                logging.error("cannot get Prowl response")
                logging.debug("cannot get Prowl response", exc_info=True)
                return

            finally:
                logging.debug("close Prowl-Connection")
                try:
                    request.close()
                except:
                    pass

    except:
        logging.error("unknown error")
        logging.debug("unknown error", exc_info=True)