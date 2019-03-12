# Copyright (c) 2017, 2019, DCSO GmbH

import splunk.admin as admin
import splunk.entity as en
import re
# import your required python modules

'''
Copyright (C) 2005 - 2010 Splunk Inc. All Rights Reserved.
Description:  This skeleton python script handles the parameters in the configuration page.

      handleList method: lists configurable parameters in the configuration page
      corresponds to handleractions = list in restmap.conf

      handleEdit method: controls the parameters and saves the values
      corresponds to handleractions = edit in restmap.conf

'''

class ConfigApp(admin.MConfigHandler):
  '''
  Set up supported arguments
  '''
  def setup(self):
    if self.requestedAction == admin.ACTION_EDIT:
      for arg in ['host','port','user','password']:
        self.supportedArgs.addOptArg(arg)

  '''
  Read the initial values of the parameters from the custom file
      myappsetup.conf, and write them to the setup page.

  If the app has never been set up,
      uses .../app_name/default/myappsetup.conf.

  If app has been set up, looks at
      .../local/myappsetup.conf first, then looks at
  .../default/myappsetup.conf only if there is no value for a field in
      .../local/myappsetup.conf

  For boolean fields, may need to switch the true/false setting.

  For text fields, if the conf file says None, set to the empty string.
  '''

  def handleList(self, confInfo):
    confDict = self.readConf("dcso_tie_setup")
    if None != confDict:
      for stanza, settings in confDict.items():
        for key, val in settings.items():
          if key in ['host','port','user','password'] and val in [None, '']:
            val = ''
          confInfo[stanza].append(key, val)

  '''
  After user clicks Save on setup page, take updated parameters,
  normalize them, and save them somewhere
  '''
  def handleEdit(self, confInfo):
    name = self.callerArgs.id
    args = self.callerArgs

    if self.callerArgs.data['host'][0] is None:
      self.callerArgs.data['host'][0] = ''
    if self.callerArgs.data['port'][0] is None:
      self.callerArgs.data['port'][0] = ''
    if self.callerArgs.data['user'][0] is None:
      self.callerArgs.data['user'][0] = ''
    if self.callerArgs.data['password'][0] is None:
      self.callerArgs.data['password'][0] = ''



    '''
    Since we are using a conf file to store parameters,
write them to the [setupentity] stanza
    in app_name/local/myappsetup.conf
    '''

    self.writeConf('dcso_tie_setup', 'proxy', self.callerArgs.data)

# initialize the handler
admin.init(ConfigApp, admin.CONTEXT_NONE)
