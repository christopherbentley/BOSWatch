#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Prowl-Plugin to send FMS-, ZVEI- and POCSAG - messages to Prowl
@author: Marco Grosjohann
@requires: Prowl-Configuration has to be set in the config.ini
"""

import logging  # Global logger
import httplib  # for the HTTP request
import urllib
from includes import globalVars  # Global variables

# from includes.helper import timeHandler
from includes.helper import configHandler
from includes.helper import wildcardHandler


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
    """
    # nothing to do for this plugin
    return


##
#
# Main function of Prowl-plugin
# will be called by the alarmHandler
#
def run(typ, freq, data):
    """
    This function is the implementation of the Prowl-Plugin.
    It will send the data to Prowl API
    @type    typ:  string (FMS|ZVEI|POC)
    @param   typ:  Typ of the dataset
    @type    data: map of data (structure see readme.md in plugin folder)
    @param   data: Contains the parameter
    @type    freq: string
    @keyword freq: frequency of the SDR Stick
    @requires:  Prowl-Configuration has to be set in the config.ini
    @return:    nothing
    """
    try:
        if configHandler.checkConfig("Prowl"):  # read and debug the config

            if typ == "FMS":
                #
                # building message for FMS
                #
                text = globalVars.config.get("Prowl", "fms_text")
                title = globalVars.config.get("Prowl", "fms_title")
                priority = globalVars.config.get("Prowl", "fms_prio")

            elif typ == "ZVEI":
                #
                # building message for ZVEI
                #
                text = globalVars.config.get("Prowl", "zvei_text")
                title = globalVars.config.get("Prowl", "zvei_title")
                priority = globalVars.config.get("Prowl","zvei_std_prio")

            elif typ == "POC":
                #
                # building message for POC
                #
                if data["function"] == '1':
                    priority = globalVars.config.get("Prowl", "SubA")
                elif data["function"] == '2':
                    priority = globalVars.config.get("Prowl", "SubB")
                elif data["function"] == '3':
                    priority = globalVars.config.get("Prowl", "SubC")
                elif data["function"] == '4':
                    priority = globalVars.config.get("Prowl", "SubD")
                else:
                    priority = ''
                        
                text = globalVars.config.get("Prowl", "poc_text")
                title = globalVars.config.get("Prowl", "poc_title")

            else:
                logging.warning("Invalid type: %s", typ)
                return

        try:
            #
            # Prowl-Request
            #
            logging.debug("send Prowl for %s", typ)

            # replace the wildcards
            text = wildcardHandler.replaceWildcards(text, data)
            title = wildcardHandler.replaceWildcards(title, data)
            
            # Logging data to send
            logging.debug("Title   : %s", title)
            logging.debug("Text    : %s", text)
            logging.debug("Priority: %s", priority)

            # start the connection
            conn = httplib.HTTPSConnection("api.prowlapp.com:443")
            conn.request("GET", "/publicapi/add",
                        urllib.urlencode({
                            "accesskey": globalVars.config.get("Prowl", "accesskey"),
                            "title": title,
                            "text": text,
                            "priority": priority,
                        }))

        except:
            logging.error("cannot send Prowl request")
            logging.debug("cannot send Prowl request", exc_info=True)
            return

        try:
            #
            # check Prowl-Response
            #
            response = conn.getresponse()
            if str(response.status) == "200":  # Check Prowl Response and print a Log or Error
                logging.debug("Prowl response: %s - %s", str(response.status), str(response.reason))
            else:
                logging.warning("Prowl response: %s - %s", str(response.status), str(response.reason))
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
