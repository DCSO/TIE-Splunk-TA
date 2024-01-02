DCSO Threat Intelligence Engine (TIE) Add-On for Splunk
=======================================================

Copyright (c) 2015, 2023, DCSO Deutsche Cyber-Sicherheitsorganisation GmbH

Splunk add-on for the DCSO Threat Intelligence Engine (TIE) which fetches IoCs (Indicator of Compromise)
and stores them into a Splunk index.

# Prerequisites and Installation

Most of the AddOn's functionality can be used and tested without having Splunk installed.

* Python v3.7 or greater.
* Splunk Enterprise 8 or greater.
* DCSO API credentials.
* Connection from your Splunk instance(s) to https://api.dcso.de (check your firewall setup)

## Installation

You can install the DCSO TIE AddOn within the Splunk Enterprise Web interface:

1. click on the `splunk>enterprise`-logo
2. click on the wheel next to 'Apps'
3. click 'Install app from file'
4. choose the file, navigating to the folder on your local machine containing a file called like `DCSO_TIE_Splunk_AddOn3-3.0.0.zip`
5. if you are upgrading, make sure to check 'Upgrade app'
6. click 'Upload'

You can also install the add-on through the Splunk CLI (Command Line Interface):

```
${SPLUNK_HOME}/bin/splunk install app DCSO_TIE_Splunk_AddOn3-3.0.0.zip
```

# Configuration

After installation, the add-on needs to be configured.

## Splunk App Setup Page

Important: when after saving an error appears in the Splunk Web tool, the configuration is stored, but
it does not give much information what went wrong.
To find out the issue, you will have to look in the log file (see below).

DCSO IDM credentials are required to access the Threat Intelligence Engine or TIE.
If you have any questions about the credentials, please contact DCSO (see below).

There are few more details about the configuration:

* **API Client ID**: DCSO IDM client_id.
* **API Client Secret**: DCSO IDM client_secret.
* **Initial IoC Update Time**: Use this to start from a particular time from where IoC were updated. 
  This should be a timestamp in RFC3339 format. This is useful when re-installing or upgrading to 
  incompatible add-on version (data in index would stay compatible). Leave 0 to use whatever data 
  is stored or start from NOW minus 30 days.
* **tie2index.py** script: make sure to enable this by un-checking the checkbox.
* **Index for IoCs**: the index used to store IoCs (events). When using a custom index, it
  must already exist.
* **Severity & Confidence**: can be provided as number as well as range (or example `1-` or `30-90`).

## Standard Filter

The default settings for the filter can be found in the file `default/dcso_tie_setup.conf` and are
filled out when setting up the add-on.

#  Usage

## Getting the IoCs

### tie2index.py

The input script `tie2index.py` will automatically start with the oldest IoC in a 30 day range. From
that it will iterate and index all updates made. The interval is by default 10 minutes (600 seconds).
All IoCs and their updates will be stored in an index (default: dcso_app_tie-api). We recommend at
least 180 days as retention time for this index. From this index all lookups and files can be derived.

To limit the used licence volume we only index IoCs within specified confidence and severity ranges.
The default ranges of the filters are mentioned in the section 'Standard Filter'.

## Logging

This add-on will log errors, warnings, and other informative messages to a separate log file within
the folder `${SPLUNK_HOME}/var/log/splunk`. The file is called `dcso_tie.log` and is rotated 6 times.

The entries in this log file are stored, when executed by Splunk, as JSON. This makes it ready to be
monitored by Splunk itself.

# Contact

* Email: ti-support [a] dcso.de
* Website: https://dcso.de

# Development & Deployment

## Development

### Debugging the setup.xml

You can use `xmllint` to validate or check the `setup.xml` file:

```
$ xmllint /path/to/setup.xml --noout --relaxng ${SPLUNK_HOME}/share/splunk/search_mrsparkle/exposed/schema/setup.rng
```

### Running tests

Tests can be run using the following command from the root of the repository:

```shell
$ python tests/tests.py
```

## Deployment

The add-on can be packaged using the normal `distutils` command. However, for Splunk we needed
to adapt a bit so that it is easy to create, deploy and install.

## For Splunk

This add-on has it's own `distutils` command called `splunkdist`:

```shell
$ python setup.py splunkdist --format=zip
```

The above command will create a ZIP archive in the folder `dist/`. The name of the file is so that
it contains the major and full version of this add-on. The folder it unpacks too has simply the
major version, for example:

```
$ python setup.py splunkdist --format=zip

# creates:
dist/DCSO_TIE_Splunk_AddOn3-3.0.0.zip

$ unzip -l dist/DCSO_TIE_Splunk_AddOn3-3.0.0.zip
Archive:  dist/DCSO_TIE_Splunk_AddOn3-3.0.0.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  05-26-2020 13:36   DCSO_TIE_AddOn3/
        0  05-26-2020 13:36   DCSO_TIE_AddOn3/bin/
        0  05-26-2020 13:36   DCSO_TIE_AddOn3/default/
        0  05-26-2020 13:36   DCSO_TIE_AddOn3/static/
...
```

# License

See LICENSE file included in the repository.
