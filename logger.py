import logging

class PyLogger(object):
    def __init__(self, logname,log_level=logging.DEBUG):
        logging.basicConfig(filename=logname,filemode='w', format='[%(asctime)s] %(levelname)s: %(name)s: %(message)s',level=log_level,datefmt='%d-%m-%Y %H:%M:%S %p')
        self.logger = logging.getLogger('tp_process_logger')  

    def info(self,text):
        self.logger.info(text)

    def debug(self,text):
        self.logger.debug(text)

    def error(self,text):
        self.logger.error(text)
        
    def warning(self,text):
        self.logger.warning(text)