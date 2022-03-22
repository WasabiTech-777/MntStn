import re
import os
import xml.etree.ElementTree as ET
from Settings.setup_logger import logging

logger = logging.getLogger(__name__)

class helper:
    def downloadEdgarIndexFileAndGetPath(response, qtr, year):
        edgarIndexFileDownloadPath = f"{os.path.dirname(__file__)}\\resources\edgar-full-index-archives\master-{year}-QTR{qtr}.txt"
        logger.info(f"Downloading the master Edgar Index File to: {edgarIndexFileDownloadPath}")

        with open(edgarIndexFileDownloadPath, "wb") as f:
            f.write(response.content)
        if not f.closed:
            try:
                os.remove(edgarIndexFileDownloadPath)
            except OSError as e:  
                logger.info("Error downloading and processing the Edgar Index file - rerun as it now most likely contains corrupted data: %s - %s." % (e.filename, e.strerror))

        return edgarIndexFileDownloadPath

    def process_13f_hr_subtree(self, subtree, out_file):
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

    def process_13f_hr(self, filingFile):

        pattern = b'<(.*?)informationTable\s|<informationTable'
        matchInformationTableStart = re.search(pattern, filingFile.content)

        pattern2 = b'</(\w*):informationTable>|</informationTable>.*?'
        match2InformationTableEnd = re.search(pattern2, filingFile.content)

        fileByteString = filingFile.content[matchInformationTableStart.start() : match2InformationTableEnd.end()]
        root = ET.fromstring(fileByteString.decode())

        with open("Apps/Collection/src/resources/13F-HR-parsed-data.csv", 'a') as out_file:
                for child in root:
                    self.process_13f_hr_subtree(child, out_file)

    def process_10k(filingFile, secApi):
        with open("Apps/Collection/src/resources/10-K-parsed-data.csv", 'a') as out_file:
                for file in filingFile.json()['directory']['item']:
                    if file['name'] == 'FilingSummary.xml':
                        xmlSummary = secApi.baseUrl + filingFile.json()['directory']['name'] + "/" + file['name']
                        logger.info('filePath: ' + xmlSummary)