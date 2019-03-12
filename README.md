DCSO Threat Intelligence Engine (TIE) Technical Add-on for Splunk
==================================================================
Splunk technical add-on (TA) for DCSO Threat Intelligence Engine (TIE).

Copyright (c) 2015, 2019, DCSO Deutsche Cyber-Sicherheitsorganisation GmbH

# 1. Prerequisites and Installation
* The default python major version of 
  * 7.1.2 is Python 2.7.x
  * 7.2.4 is Python 2.7.x
* All required python packages are pre-installed from Splunk itself. 
  * If any package is missing please open an issue to us and try to do: `pip install -r requirements.txt --no-cache`

## 1.1 Prerequisites
* Splunk
* Customer for the DCSO TI-Aggregation Package
* Generate an Token in the settings page of [TIE web interface](https://tie.dcso.de) with the following privileges:
  * tie
  * tie:pingback
* Firewall Requirements
  
    | Source                           | Destination | Protocol | Port | Comment    |
    | -------------------------------- | ----------- | -------- | ---- | ---------- |
    | \<Your Splunk server IP with the installed TA\> | tie.dcso.de | TCP      | 443  | API access |


## 1.2 Installation
This app must be installed on a **Heavy Forwarder** with an internet connection to reach the  [API](https://tie.dcso.de). 

# 2. Configuration

## 2.1 Splunk Setup Page
An access token is required for the API access. If you are already a customer and do not have one, please do not hesitate to contact us. If you are not a customer yet, please feel free to contact us for a demo account.

Contact Mail: ti-support [a] dcso.de

The token has to be configured in the setup page of the technical add-on on the Splunk HF. You also have to enable the script by `unchecking` the "tie2index.py" box. There are also options for the schedule and the Index where the IoC's are stored. The Index must be known on the HF.

## 2.2 Standard Filter

The default settings for the filter you find in default/dcso_tie_setup.conf


# 3. Usage

## 3.1 Getting the IoCs

### 3.1.1 tie2index

The input script tie2index.py will automatically start with the oldest IoC in a 30 day range. From that it will iterate and index all updates made. The intervall is by default 10 minutes. All IoC and their update will be stored in an index (default: dcso_app_tie-api). We recommend at least 180 days as retention time for this index. From this index all lookups and files can be derived.

To limit the used licence volume we only index IoCs within specified confidence and severity ranges. The ranges in the filter mentioned above are default.


# Contact
Mail: ti-support [a] dcso.de

Website: https://dcso.de

# License
Please have a look at the LICENSE file included in the repository.
