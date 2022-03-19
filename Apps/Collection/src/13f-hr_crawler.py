import itertools
import logging
import os
import re
import time
import xml.etree.ElementTree as ET
from src.api.sec_api import SecAPI
from src.helper import helper

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

#TODO: refactor
yr = '2022'
qtr = '1'

response = SecAPI().getMasterEdgarIndexFileByQtrAndYrApi(qtr, yr)
edgarIndexFilePath = helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)
fileCounter = 0

def process_subtree(subtree, out_file):
    nameOfIssuer = ''
    cusip = ''
    value = ''
    shares = ''
    sshPrnamtType = ''
    investmentDiscretion = ''
    putCall = ''
    otherManager = ''
    soleVotingAuthority = ''
    sharedVotingAuthority = ''
    noneVotingAuthority = ''

    for child in subtree:
        startIndex = child.tag.find('}')
        childTag = child.tag[startIndex + 1: ]
        if ((child.text == None) and (isinstance(child.attrib, dict)) and (isinstance(child, ET.Element)) or (child.text.isspace())) :
            for nestedChild in child:
                startIndex = nestedChild.tag.find('}')
                nestedChildTag = nestedChild.tag[startIndex + 1: ]
                match nestedChildTag:
                    case 'sshPrnamt':
                        shares = nestedChild.text
                    case 'sshPrnamtType':
                        sshPrnamtType = nestedChild.text
                    case 'Sole':
                        soleVotingAuthority = nestedChild.text
                    case 'Shared':
                        sharedVotingAuthority = nestedChild.text
                    case 'None':
                        noneVotingAuthority = nestedChild.text
        else:
            match childTag:
                case 'nameOfIssuer':
                    nameOfIssuer = child.text
                case 'cusip':
                    cusip = child.text
                case 'value':
                    value = child.text
                case 'investmentDiscretion':
                    investmentDiscretion = child.text
                case 'putCall':
                    putCall = child.text
                case 'otherManager':
                    otherManager = child.text

    nameOfIssuer = nameOfIssuer.replace(",", "")
    line = nameOfIssuer + ',' + cusip + ',' + value + ',' + shares + ',' + sshPrnamtType + ',' + putCall + ',' + investmentDiscretion + "," + otherManager + ',' + soleVotingAuthority + ',' + sharedVotingAuthority + ',' + noneVotingAuthority + "\n"
    out_file.write(line)

with open(edgarIndexFilePath) as file:
    for line in itertools.islice(file, 11, None):
        splitLineCompanyInfo = line.strip().split("|")
        if(splitLineCompanyInfo[2] == "13F-HR"):
            fileCounter +=1
            # Current max request rate: 10 requests/second per SEC - https://www.sec.gov/os/accessing-edgar-data 
            filingFile = SecAPI().get13FHRFilingForCompanyApi(splitLineCompanyInfo)
            time.sleep(1/10)

            pattern = b'<(.*?)informationTable\s|<informationTable'
            matchInformationTableStart = re.search(pattern, filingFile.content)

            pattern2 = b'</(\w*):informationTable>|</informationTable>.*?'
            match2InformationTableEnd = re.search(pattern2, filingFile.content)

            fileByteString = filingFile.content[matchInformationTableStart.start() : match2InformationTableEnd.end()]
            root = ET.fromstring(fileByteString.decode())

            LOGGER.info(f"Processing 13F-HR for : {splitLineCompanyInfo[1]}\n")

            with open("src/resources/13F-HR-parsed-data.csv", 'a') as out_file:
                for child in root:
                    process_subtree(child, out_file)

LOGGER.info("Processed " + str(fileCounter) + " 13F-HR files in master file.")