DCSO Threat Intelligence Engine (TIE) Add-On for Splunk
=======================================================

Copyright (c) 2015, 2020, DCSO Deutsche Cyber-Sicherheitsorganisation GmbH

Splunk add-on for the DCSO Threat Intelligence Engine (TIE) which fetches IoCs (Indicator of Compromise)
and stores them into a Splunk index.

# Prerequisites and Installation

Most of the AddOn's functionality can be used and tested without having Splunk installed.

* Python v3.7 or greater.
* Splunk Enterprise 8 or greater.
* DCSO TIE (legacy) or Portal API token.
* Connection from your Splunk instance(s) to https://tie.dcso.de:443 (check your firewall setup)


## Installation

You can install the DCSO TIE AddOn within the Splunk Enterprise Web interface:

1. click on the `splunk>enterprise`-logo
2. click on the wheel next next to 'Apps'
3. click 'Install app from file'
4. choose the file, navigating to the folder on your local machine containing a file called like `DCSO_TIE_Splunk_AddOn2-2.0.0b5.zip`
5. if you are upgrading, make sure to check 'Upgrade app'
6. click 'Upload'

You can also install the add-on through the Splunk CLI (Command Line Interface):

```
${SPLUNK_HOME}/bin/splunk install app DCSO_TIE_Splunk_AddOn2-2.0.0b5.zip
```

# Configuration

After installation, the add-on needs to be configured.

## Splunk App Setup Page

After installation you must setup the app or add-on.

An API or Machine Token is required to access the Threat Intelligence Engine or TIE. Both the legacy
token created through `tie.dcso.de` and the newer tokens created through `portal.dcso.de` are supported.
If you have any questions about this Token, please contact DCSO (see below).

There are few more details about the configuration:

* **API Token**: either a legacy tie.dcso.de token, or new one created through the DCSO Portal.
* **Initial IoC Sequence Number**: Use this to start from a particular sequence number. This is
  useful when re-installing or upgrading to incompatible add-on version (data in index would
  stay compatible). Leave 0 to use whatever number is stored or start from NOW minus 30 days. 
* **tie2index.py** script: make sure to enable this by un-checking the checkbox.
* **Index for IoCs**: the index used to store IoCs (events). When using a custom index, it
  must already exist.

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

Tests requiring the DCSO TIE to be avalable are skipped when no token was provided. To run these tests,
define the environment variable `TIE_TOKEN`:

```shell
$ TIE_TOKEN=YOURTOKENHERE python tests/tests.py
```

## Deployment

The add-on can be packages using the normal `distutils` command. However, for Splunk we need
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
dist/DCSO_TIE_Splunk_AddOn2-2.0.0b6.zip

$ unzip -l dist/DCSO_TIE_Splunk_AddOn2-2.0.0b6.zip
Archive:  dist/DCSO_TIE_Splunk_AddOn2-2.0.0b6.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  05-26-2020 13:36   DCSO_TIE_AddOn2/
        0  05-26-2020 13:36   DCSO_TIE_AddOn2/bin/
        0  05-26-2020 13:36   DCSO_TIE_AddOn2/default/
        0  05-26-2020 13:36   DCSO_TIE_AddOn2/static/
...
```

# License

See LICENSE file included in the repository.

