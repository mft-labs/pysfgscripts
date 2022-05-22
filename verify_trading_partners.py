from requests.auth import HTTPBasicAuth
import requests
import traceback
import os, json, sys
import argparse

class VerifyTradingPartners(object):
    def __init__(self,partnerslist):
        self.log_file = open('verify-partners.log','w')
        self.report=open('tp-report.csv','w')
        self.report.write('"Partner name","Status"')
        self.report.write('\n')
        self.partnerslist = partnerslist
        self.props = self.get_properties()
        self.baseurl = self.props['SFG_API_BASEURL']
        #self.username = self.props['SFG_API_USERNAME']
        #self.password = self.props['SFG_API_PASSWORD']
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.auth = HTTPBasicAuth(self.props['SFG_API_USERNAME'], self.props['SFG_API_PASSWORD'])
        #self.partners_url = '/B2BAPIs/svc/tradingpartners/'
        #self.rc_url = '/B2BAPIs/svc/routingchannels/'
        self.partners_url = '/tradingpartners/'
        self.rc_url = '/routingchannels/'

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

    def verify_tps(self):
        for partner in self.partnerslist:
            try:
                if partner.strip() == '':
                    continue
                details = self.get_partner_details(partner)
                if details != None:
                    self.log_file.write(f'##FOUND: {partner} exists, details are {details}')
                    self.log_file.write('\n')
                    self.report.write(f'"{partner}","Found"')
                else:
                    self.log_file.write(f'##NOT_FOUND: {partner} cleared successfully')
                    self.log_file.write('\n')
                    self.report.write(f'"{partner}","Not Found"')
                self.report.write('\n')
            except:
                self.log_file(f'Failed verify for {partner}, or cleared {traceback.format_exc()}')
        self.log_file.close()
        self.report.close()

    def get_partner_details(self, partner):
        self.log_file.write(f'##LOG: Going to find the details of partner {partner}')
        self.log_file.write('\n')
        res = requests.get(f'{self.baseurl}{self.partners_url}/{partner}',auth=self.auth, headers=self.headers)
        if res.status_code == 200:
            return res.json()
        if res.status_code == 404:
            return None
        self.log_file.write(f'##LOG: [get_partner_details] Status returned:{res.status_code}')
        self.log_file.write('\n')
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--infile',
                    dest='filename',
                    help='File containing partners list'
                    )
    args = parser.parse_args()
    
    #filename = sys.argv[1]
    partnerslist = open(args.filename,'r').read().split('\n')
    app = VerifyTradingPartners(partnerslist)
    app.verify_tps()