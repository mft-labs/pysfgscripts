from requests.auth import HTTPBasicAuth
import requests
import traceback
import os, json, sys
import argparse

class CleanTradingPartners(object):
    def __init__(self,partnerslist):
        self.partnerslist = partnerslist
        self.props = self.get_properties()
        self.baseurl = self.props['SFG_API_BASEURL']
        #self.username = self.props['SFG_API_USERNAME']
        #self.password = self.props['SFG_API_PASSWORD']
        self.  headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.auth = HTTPBasicAuth(self.props['SFG_API_USERNAME'], self.props['SFG_API_PASSWORD'])
        self.partners_url = '/B2BAPIs/svc/tradingpartners/'
        self.rc_url = '/B2BAPIs/svc/routingchannels/'

    def get_properties(self):
        pfile = os.environ["AMF_SFG_HOME"]+"/properties/sfgutils.properties"
        pmap = {}
        d = open(pfile, 'r').read()
        for line in d.split('\n'):
            line = line.strip()
            if line.startswith("#"):
                continue
            vals = line.split("=", 1)
            if len(vals) == 2:
                key = vals[0].strip()
                val = vals[1].strip()
                pmap[key] = val
        return pmap
    
    def verify_and_delete_tp(self):
        for partner in self.partnerslist:
            details = self.get_partner_details(partner)
            if details != None:
                print(f"Authentication Type: {details['authenticationType']['code']}")
                #print(details)
                if details['authenticationType']['code'] == 'Local':
                    print(f'{partner} is local')
                    rc_list = self.find_routing_channel(details['_id'])
                    routing_channel_deleted = False
                    if rc_list != None and len(rc_list) > 0 :
                        for rc in rc_list:
                            #print(f'Going to delete routing channel {rc}')
                            success = self.delete_routing_channel(rc)
                            if success:
                                print(f"{rc['_id']} deleted successfully")
                            else:
                                print(f"Failed to delete routing channel {rc['_id']}")
                        routing_channel_deleted = True
                    elif rc_list != None and len(rc_list) == 0 :
                        print(f'No routing channel found for {partner}')
                        routing_channel_deleted = True
                    else:
                        print(f"Routing channel retrieval failed ({details['_id']})") 
                    if routing_channel_deleted:
                        success2 = self.delete_trading_partner(partner)
                        if success2:
                            print(f'Deleted trading partner {partner} successfully')
                        else:
                            print(f'Failed to delete trading partner {partner}')
                else:
                    print(f"{partner} is not an internal user (authentication type is not local)")
            else:
                print(f'{partner} not found')
        
    def get_partner_details(self, partner):
        print(f'Going to find the details of partner {partner}')
        res = requests.get(f'{self.baseurl}{self.partners_url}/{partner}',auth=self.auth, headers=self.headers)
        if res.status_code == 200:
            return res.json()
        print(f'[get_partner_details] Status returned:{res.status_code} and response {res.text}')
        return None

    def find_routing_channel(self,sfgid):
        res = requests.get(f'{self.baseurl}{self.rc_url}/?searchByConsumer=&searchByTemplate=&searchByProducer={sfgid}',auth=self.auth, headers=self.headers)
        if res.status_code == 200:
            return res.json()
        if res.status_code == 404:
            return []
        print(f'[find_routing_channel] Status returned:{res.status_code} and response {res.text}')
        return None

    def delete_routing_channel(self,rc):
        print(f"Deleting routing channel with id {rc['_id']}")
        res = requests.delete(f"{self.baseurl}{self.rc_url}/{rc['_id']}",auth=self.auth, headers=self.headers)
        if res.status_code == 200:
            return True
        print(f'[delete_routing_channel] Status returned:{res.status_code} and response {res.text}')
        return False

    def delete_trading_partner(self,partner):
        res = requests.delete(f'{self.baseurl}{self.partners_url}/{partner}',auth=self.auth, headers=self.headers)
        if res.status_code == 200:
            return True
        print(f'[delete_trading_partner] Status returned:{res.status_code} and response {res.text}')
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--infile',
                    dest='filename',
                    help='File containing partners list'
                    )
    args = parser.parse_args()
    
    #filename = sys.argv[1]
    partnerslist = open(args.filename,'r').read().split('\n')
    app = CleanTradingPartners(partnerslist)
    app.verify_and_delete_tp()
