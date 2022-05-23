from requests.auth import HTTPBasicAuth
import requests
import traceback
import os, json, sys
import argparse
from logger import PyLogger
from datetime import datetime
import time

class CleanTradingPartners(object):
    def __init__(self,partnerslist):
        now = datetime.now()
        self.logger = PyLogger('clean_tp_{}.log'.format(now.strftime('%Y%b%d_%H%M%S')))
        self.partnerslist = partnerslist
        self.props = self.get_properties()
        self.baseurl = self.props['SFG_API_BASEURL']
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.auth = HTTPBasicAuth(self.props['SFG_API_USERNAME'], self.props['SFG_API_PASSWORD'])
        #self.partners_url = '/B2BAPIs/svc/tradingpartners/'
        #self.rc_url = '/B2BAPIs/svc/routingchannels/'
        self.partners_url = '/tradingpartners/'
        self.rc_url = '/routingchannels/'

    def get_properties(self):
        self.logger.debug('Reading profiles from sfgutils')
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
        self.logger.debug('Going to run cleanup process')
        for partner in self.partnerslist:
            try:
                if partner.strip() == '':
                    continue
                self.logger.debug(f'Retrieving details of {partner} from SFG')
                details = self.get_partner_details(partner)
                if details != None:
                    self.logger.debug(f"Authentication Type: {details['authenticationType']['code']}")
                    #print(details)
                    deletion_failed = False
                    if details['authenticationType']['code'] == 'Local':
                        self.logger.debug(f'{partner} is local')
                        rc_list = self.find_routing_channel(details['_id'])
                        routing_channel_deleted = False
                        if rc_list != None and len(rc_list) > 0 :
                            for rc in rc_list:
                                #print(f'Going to delete routing channel {rc}')
                                success = self.delete_routing_channel(rc)
                                if success:
                                    self.logger.debug(f"{rc['_id']} deleted successfully")
                                    #driver = CasUtil(partner)
                                    #driver.delete_step1()
                                    #driver.delete_step2()
                                    #driver.delete_step3()
                                    #driver.delete_step4()
                                else:
                                    self.logger.debug(f"Failed to delete routing channel {rc['_id']}")
                                    deletion_failed = True
                            routing_channel_deleted = True
                        elif rc_list != None and len(rc_list) == 0 :
                            #driver = CasUtil(partner)
                            #driver.delete_step1()
                            #driver.delete_step2()
                            #driver.delete_step3()
                            #driver.delete_step4()
                            self.logger.debug(f'No routing channel found for {partner}')
                            routing_channel_deleted = True
                        else:
                            self.logger.debug(f"Routing channel retrieval failed ({details['_id']})") 
                        if routing_channel_deleted and not deletion_failed:
                            success2 = self.delete_trading_partner(partner)
                            if success2:
                                self.logger.debug(f'Deleted trading partner {partner} successfully')
                            else:
                                self.logger.debug(f'Failed to delete trading partner {partner}')
                    else:
                        self.logger.debug(f"{partner} is not an internal user (authentication type is not local)")
                else:
                    self.logger.debug(f'{partner} not found')
            except:
                self.logger.error(f'Failed process for {partner} {traceback.format_exc()}')
        
    def get_partner_details(self, partner):
        print(f'Going to find the details of partner {partner}')
        res = requests.get(f'{self.baseurl}{self.partners_url}/{partner}',auth=self.auth, headers=self.headers, verify=False)
        if res.status_code == 200:
            return res.json()
        print(f'[get_partner_details] Status returned:{res.status_code} and response {res.text}')
        return None

    def find_routing_channel(self,sfgid):
        res = requests.get(f'{self.baseurl}{self.rc_url}/?searchByConsumer=&searchByTemplate=&searchByProducer={sfgid}',auth=self.auth, headers=self.headers, verify=False)
        if res.status_code == 200:
            return res.json()
        if res.status_code == 404:
            return []
        print(f'[find_routing_channel] Status returned:{res.status_code} and response {res.text}')
        return None

    def delete_routing_channel(self,rc):
        print(f"Deleting routing channel with id {rc['_id']}")
        res = requests.delete(f"{self.baseurl}{self.rc_url}/{rc['_id']}",auth=self.auth, headers=self.headers, verify=False)
        if res.status_code == 200 or res.status_code == 404:
            return True
        if res.status_code == 400 and 'API000102: Error deleting a part of the Routing Channel' in res.text:
            return True
        print(f'[delete_routing_channel] Status returned:{res.status_code} and response {res.text}')
        return False

    def delete_trading_partner(self,partner):
        res = requests.delete(f'{self.baseurl}{self.partners_url}/{partner}',auth=self.auth, headers=self.headers, verify=False)
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
