# Copyright (c) 2017, 2023, DCSO GmbH

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
    def setup(self):
        """
        Set up supported arguments
        """
        if self.requestedAction == admin.ACTION_EDIT:
            for arg in [
                "ip_confidence",
                "ip_severity",
                "dom_confidence",
                "dom_severity",
                "url_confidence",
                "url_severity",
                "email_confidence",
                "email_severity",
                "confidence",
                "severity",
            ]:
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
                    if (
                        key
                        in [
                            "ip_confidence",
                            "ip_severity",
                            "dom_confidence",
                            "dom_severity",
                            "url_confidence",
                            "url_severity",
                            "email_confidence",
                            "email_severity",
                            "confidence",
                            "severity",
                        ]
                        and val in [None, ""]
                    ):
                        val = ""
                    confInfo[stanza].append(key, val)

    # After user clicks Save on setup page, take updated parameters,
    # normalize them, and save them somewhere
    def handleEdit(self, confInfo):
        name = self.callerArgs.id
        args = self.callerArgs

        if args.data["ip_confidence"][0] is None:
            args.data["ip_confidence"][0] = ""
        if args.data["ip_severity"][0] is None:
            args.data["ip_severity"][0] = ""
        if args.data["dom_confidence"][0] is None:
            args.data["dom_confidence"][0] = ""
        if args.data["dom_severity"][0] is None:
            args.data["dom_severity"][0] = ""
        if args.data["url_confidence"][0] is None:
            args.data["url_confidence"][0] = ""
        if args.data["url_severity"][0] is None:
            args.data["url_severity"][0] = ""
        if args.data["email_confidence"][0] is None:
            args.data["email_confidence"][0] = ""
        if args.data["email_severity"][0] is None:
            args.data["email_severity"][0] = ""
        if args.data["confidence"][0] is None:
            args.data["confidence"][0] = ""
        if args.data["severity"][0] is None:
            args.data["severity"][0] = ""

        # Since we are using a conf file to store parameters, write them to the [setupentity] stanza
        # in app_name/local/myappsetup.conf
        self.writeConf("dcso_tie_setup", "filter", self.callerArgs.data)


# initialize the handler
admin.init(ConfigApp, admin.CONTEXT_NONE)
