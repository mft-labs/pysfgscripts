from cassandra.cluster import Cluster
import ssl

class CasUtil(object):
    def __init__(self,mailbox):
        self.cluster = Cluster(['192.168.25.250'],port=9042,connection_class=None,
                            ssl_options=dict(ca_certs='<certfile>',
                                   cert_reqs=ssl.CERT_REQUIRED,
                                   ssl_version=ssl.PROTOCOL_TLSv1))
        self.session = self.cluster.connect('mailbox',wait_for_all_pools=True)
        self.details = {}
        self.details = self.get_details(mailbox)
        self.details['mailbox'] = mailbox
        self.details2 = self.get_app_info(self.details['mailbox_id'])

    def get_details(self,mailbox):
        rows = self.session.execute(f"select * from event_rule_mailboxes where mailbox_path = '/{mailbox}' ALLOW FILTERING")
        info = {}
        for row in rows:
            info['id'] = row.id
            info['mailbox_id'] = row.mailbox_id
            print(f'Mailbox details retrieved for {mailbox} is {info}')
            return info
        return None

    def delete_step1(self):
        if self.details != None:
            id = self.details['id']
            result = self.session.execute(f"""delete from event_rule_mailboxes where mailbox_path = '/{self.details["mailbox"]}' and id = {id} ;""")

    def delete_step2(self):
        if self.details != None:
            mailbox_id = self.details['mailbox_id']
            result = self.session.execute(f"delete from mailbox_event_rules where  mailbox_id = {mailbox_id};")

    def delete_step3(self):
        print(f'Going to delete from application events with {self.details}')
        if self.details2 != None:
            print(f'Found details of app {self.details2}')
            app_id = self.details2['app_id']
            uc_rule_name =  self.details2['uc_rule_name']
            print(f'Details used for deleting {app_id} and {uc_rule_name}')
            result = self.session.execute(f"delete from application_event_rules where app_id = {app_id} and uc_rule_name = '{uc_rule_name}';")
        else:
            print(f'Details from app info found none for {self.details["mailbox_id"]}')

    def delete_step4(self):
        if self.details != None:
            id = self.details['id']
            result = self.session.execute(f"delete from event_rules where id = {id} ;")

    def get_app_info(self,mailbox_id):
        rows = self.session.execute(f"select app_id,uc_rule_name from mailbox_event_rules where mailbox_id = {mailbox_id} ALLOW FILTERING")
        info = {}
        for row in rows:
            info['app_id'] = row.app_id
            info['uc_rule_name'] = row.uc_rule_name
            print(f'App Info retrieved for {mailbox_id} returned {info}')
            return info
        return None
    
    def close_session(self):
        self.session.close()

if __name__ == "__main__":
    
    #session.execute('USE cityinfo')
    rows = session.execute('select * from event_rule_mailboxes')
    for row in rows:
        print(row)