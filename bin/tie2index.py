# Copyright (c) 2017, 2019, DCSO GmbH

import csv
import datetime
import json
import os
import re
import sys

import urllib2
from splunk.clilib import cli_common as cli

csv.field_size_limit(sys.maxsize)
proxy_args = cli.getConfStanza('dcso_tie_setup','proxy')

if str(proxy_args['host']):
    proxy_link = "https://{}:{}@{}:{}".format(str(proxy_args['user']),str(proxy_args['password']),str(proxy_args['host']),str(proxy_args['port']))
    proxy = urllib2.ProxyHandler({'https': proxy_link})
    auth = urllib2.HTTPBasicAuthHandler()
    opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
    urllib2.install_opener(opener)

#Check if there already is a seq.json otherwise create
#if os.path.exists(os.path.join(os.path.dirname(__file__),'../local/seq.json')):
#    with open(os.path.join(os.path.dirname(__file__),'../local/seq.json'), 'r') as seqinput:
#        seqfile = json.load(seqinput)
#else:
#    data = {'tie':{'seq_number': 0}}
#    with open(os.path.join(os.path.dirname(__file__),'../local/seq.json'), 'w') as outfile:
#        json.dump(data,outfile)

def first_run():
    period = (datetime.date.today() - datetime.timedelta(30)).strftime('%Y-%m-%dT%H:%M:%SZ')
    request = urllib2.Request("{}?first_seen_at={}&order_by=seq&direction=asc".format(TIE_API,period))
    request.add_header("X-Authorization", 'bearer {}'.format(TIE_TOKEN))
    request.add_header("Accept", 'application/json')
    contents = json.loads(urllib2.urlopen(request).read())
    try:
        if re.search("rel=next",urllib2.urlopen(request).info().getheader('Link')):
            has_more = True
        else:
            has_more = False
    except Exception as e:
        has_more = False
        print e
    return contents,has_more

def query_tie(seq):
    request = urllib2.Request("{}?seq={}-&order_by=seq&direction=asc&limit=1000".format(TIE_API,seq))
    request.add_header("X-Authorization", 'bearer {}'.format(TIE_TOKEN))
    request.add_header("Accept", 'application/json')
    contents = json.loads(urllib2.urlopen(request).read())
    try:
        if re.search("rel=next",urllib2.urlopen(request).info().getheader('Link')):
            has_more = True
        else:
            has_more = False
    except:
        has_more = False
    return contents,has_more

if __name__ == "__main__":
    #Check if there already is a seq.json otherwise create
    if os.path.exists(os.path.join(os.path.dirname(__file__),'../local/seq.json')):
        with open(os.path.join(os.path.dirname(__file__),'../local/seq.json'), 'r') as seqinput:
            seqfile = json.load(seqinput)
    else:
        seqfile = {'tie':{'seq_number': 0}}
        with open(os.path.join(os.path.dirname(__file__),'../local/seq.json'), 'w') as outfile:
            json.dump(seqfile, outfile)

    tie_args = cli.getConfStanza('dcso_tie_setup','tie')
    filter_args = cli.getConfStanza('dcso_tie_setup','filter')
    proxy_args = cli.getConfStanza('dcso_tie_setup','proxy')

    TIE_TOKEN = str(tie_args["token"])
    TIE_API = str(tie_args["feed_api"])
    
    FILTER_IP_CONFIDENCE = str(filter_args['ip_confidence'])
    FILTER_IP_SEVERITY = str(filter_args['ip_severity'])
    FILTER_URL_CONFIDENCE = str(filter_args['url_confidence'])
    FILTER_URL_SEVERITY = str(filter_args['url_severity'])
    FILTER_DOM_CONFIDENCE = str(filter_args['dom_confidence'])
    FILTER_DOM_SEVERITY = str(filter_args['dom_severity'])
    FILTER_CONFIDENCE = str(filter_args['confidence'])
    FILTER_SEVERITY = str(filter_args['severity'])
    
    i = 0
    while True:
        i += 1
        if seqfile['tie']['seq_number'] == 0:
            content,has_more = first_run()
        else:
            content,has_more = query_tie(seqfile['tie']['seq_number'])
        iocs = content["iocs"]
        for ioc in iocs:
            if (ioc['data_type']=="IPv4" and int(ioc['max_confidence']) >= int(FILTER_IP_CONFIDENCE) and int(ioc['max_severity']) >= int(FILTER_IP_SEVERITY)) or (ioc['data_type']=="URLVerbatim" and int(ioc['max_confidence']) >= int(FILTER_URL_CONFIDENCE) and int(ioc['max_severity']) >= int(FILTER_URL_SEVERITY)) or (ioc['data_type']=="DomainName" and int(ioc['max_confidence']) >= int(FILTER_DOM_CONFIDENCE) and int(ioc['max_severity']) >= int(FILTER_DOM_SEVERITY)) or (int(ioc['max_confidence']) >= int(FILTER_CONFIDENCE) and int(ioc['max_severity']) >= int(FILTER_SEVERITY)):
                print json.dumps(ioc)
            if seqfile['tie']['seq_number'] < int(ioc['min_seq']):
                seqfile['tie']['seq_number'] = int(ioc['min_seq'])+1
                with open(os.path.join(os.path.dirname(__file__),'../local/seq.json'), 'w') as save:
                    json.dump(seqfile, save)

        if not has_more or i>50:
            break
