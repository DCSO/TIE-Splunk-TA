# Copyright (c) 2017, 2020, DCSO GmbH

# This file is based on the skeleton Python script provided by Splunk.
# It is adapted to be more conform to Python code styling.

import splunk.admin as admin
# import splunk.entity as en

"""
Copyright (C) 2005 - 2010 Splunk Inc. All Rights Reserved.
Description:  This skeleton python script handles the parameters in the configuration page.

handleList method: lists configurable parameters in the configuration page
corresponds to handleractions = list in restmap.conf

handleEdit method: controls the parameters and saves the values
corresponds to handleractions = edit in restmap.conf
"""


class ConfigApp(admin.MConfigHandler):
    _supported_args = ['token', 'start_ioc_seq']
    def setup(self):
        """
        Set up supported arguments
        """
        if self.requestedAction == admin.ACTION_EDIT:
            for arg in ConfigApp._supported_args:
                self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        """
        Read the initial values of the parameters from the custom file
        myappsetup.conf, and write them to the setup page.

        If the app has never been set up, uses
            .../app_name/default/myappsetup.conf.

        If app has been set up, looks at
            .../local/myappsetup.conf first, then looks at
            .../default/myappsetup.conf only if there is no value for a field in
            .../local/myappsetup.conf

        For boolean fields, may need to switch the true/false setting.

        For text fields, if the conf file says None, set to the empty string.
        """
        confDict = self.readConf("dcso_tie_setup")
        if None != confDict:
            for stanza, settings in list(confDict.items()):
                for key, val in list(settings.items()):
                    if key in ConfigApp._supported_args and not val:
                        val = ''
                    confInfo[stanza].append(key, val)

    def handleEdit(self, confInfo):
        """
        After user clicks Save on setup page, take updated parameters,
        normalize them, and save them somewhere
        """
        name = self.callerArgs.id
        args = self.callerArgs

        if self.callerArgs.data['token'][0] is None:
            self.callerArgs.data['token'][0] = ''

        try:
            self.callerArgs.data['start_ioc_seq'][0] = str(int(self.callerArgs.data['start_ioc_seq'][0]))
        except (ValueError, TypeError):
            self.callerArgs.data['start_ioc_seq'][0] = '0'

        # Since we are using a conf file to store parameters,
        # write them to the [setupentity] stanza in app_name/local/myappsetup.conf
        self.writeConf('dcso_tie_setup', 'tie', self.callerArgs.data)


# initialize the handler
admin.init(ConfigApp, admin.CONTEXT_NONE)
