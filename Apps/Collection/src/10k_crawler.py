import itertools
import time
from api.sec_api import SecAPI
from helper import helper
from Settings.setup_logger import logging

LOGGER = logging.getLogger(__name__)

#TODO: refactor
yr = '2022'
qtr = '1'

response = SecAPI().getMasterEdgarIndexFileByQtrAndYrApi(qtr, yr)
edgarIndexFilePath = helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)
fileCounter = 0

with open(edgarIndexFilePath) as file:
    for line in itertools.islice(file, 11, None):
        splitLineCompanyInfo = line.strip().split("|")
        if(splitLineCompanyInfo[2] == "10-K"):
            fileCounter +=1
            # Current max request rate: 10 requests/second per SEC - https://www.sec.gov/os/accessing-edgar-data 
            filingFile = SecAPI().get10kFilingForCompanyApi(splitLineCompanyInfo)
            time.sleep(1/10)

            LOGGER.info(f"Processing 10-K for : {splitLineCompanyInfo[1]}\n")

            with open("resources/10-K-parsed-data.csv", 'a') as out_file:
                for file in filingFile.json()['directory']['item']:
                    if file['name'] == 'FilingSummary.xml':
                        xmlSummary = SecAPI().baseUrl + filingFile.json()['directory']['name'] + "/" + file['name']
                        LOGGER.info('filePath: ' + xmlSummary)

LOGGER.info("Processed " + str(fileCounter) + " 10-K files in master file.")