import re
import os
import xml.etree.ElementTree as ET
import pandas as pd

from IPython.display import display

from bs4 import BeautifulSoup
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
        for file in filingFile.json()['directory']['item']:
            if file['name'] == 'FilingSummary.xml':
                xmlSummary = secApi.baseUrl + filingFile.json()['directory']['name'] + "/" + file['name']
                logger.info(f"Searching through: {xmlSummary}")
                base_url = xmlSummary.replace('FilingSummary.xml', '')
                content = secApi.get(xmlSummary).content
                soup = BeautifulSoup(content, 'lxml')

                reports = soup.find('myreports')
                master_reports = []

                # loop through each report in the 'myreports' tag but avoid the last one as this will cause an error.
                for report in reports.find_all('report')[:-1]:
                    report_dict = {}
                    report_dict['name_short'] = report.shortname.text
                    report_dict['name_long'] = report.longname.text
                    report_dict['position'] = report.position.text
                    report_dict['category'] = report.menucategory.text
                    report_dict['url'] = base_url + report.htmlfilename.text
                    master_reports.append(report_dict)

                statements_url = []
                for report_dict in master_reports:
                    item1 = r"Consolidated Balance Sheets"
                    item2 = r"Consolidated Statements of Operations and Comprehensive Income (Loss)"
                    item3 = r"Consolidated Statements of Operations"
                    item4 = r"Consolidated Statements of Cash Flows"
                    item5 = r"Consolidated Statement of Changes in Stockholders' Equity and Changes in Net Assets"
                    item6 = r"Consolidated Statements of Stockholder's (Deficit) Equity"
                    report_list = [item1, item2, item3, item4, item5, item6]

                    if report_dict['name_short'] in report_list:
                        print('-'*100)
                        print(report_dict['name_short'])
                        print(report_dict['url'])
                        statements_url.append(report_dict['url'])

                statements_data = []
                for statement in statements_url:
                    statement_data = {}
                    statement_data['headers'] = []
                    statement_data['sections'] = []
                    statement_data['data'] = []
                    
                    content = secApi.get(statement).content
                    report_soup = BeautifulSoup(content, 'html.parser')

                    # find all the rows, figure out what type of row it is, parse the elements, and store in the statement file list.
                    for index, row in enumerate(report_soup.table.find_all('tr')):
                        cols = row.find_all('td')
    
                        if (len(row.find_all('th')) == 0 and len(row.find_all('strong')) == 0): 
                            reg_row = [ele.text.strip() for ele in cols]
                            print("ROW -----------------------------")
                            print(reg_row)
                            statement_data['data'].append(reg_row)
                            
                        elif (len(row.find_all('th')) == 0 and len(row.find_all('strong')) != 0):
                            sec_row = cols[0].text.strip()
                            statement_data['sections'].append(sec_row)
                            
                        elif (len(row.find_all('th')) != 0):            
                            hed_row = [ele.text.strip() for ele in row.find_all('th')]
                            statement_data['headers'].append(hed_row)
                            
                        else:            
                            logger.info("Parsed an html file with a case we haven't handled yet.")
            
                    statements_data.append(statement_data)

                print(" ============= statement_data ========================== ")
                print(" ")
                print(" ")
                print(str(statements_data))

                income_header =  statements_data[2]['headers'][0]
                income_data = statements_data[2]['data']
                #income_data = [obj['data'] for obj in statements_data]

                print(" ============= income_dftest ========================== ")
                print(" ")
                print(" ")

                income_dftest = pd.DataFrame(statements_data)

                income_dftest.to_csv('Apps/Collection/src/resources/test.csv')

                print("income_dftest")
                display(income_dftest)

                print("income data test")
                display(income_data)

                #print("income data test")
                #print(income_data)

                income_data_parsed = []
                dataLength = len(income_data[0])
                for data in income_data:
                    if len(data) != dataLength:
                        continue
                    if data[0].startswith('[1]'):
                        print("yoo")
                        print(data[0])
                        continue
                    income_data_parsed.append(data)

                print("================== income_data_parsed ===================== ")
                print((income_data_parsed))

                #print(" ")
                #print(" ")
                print(" ==================INCOME_HEADER ===================== ")
                print(" ")
                #print(" ")
                print(str(income_header))

                #print(" ")
                #print(" ")
                print(" ================== income_data ===================== ")
                #print(" ")
                print(" ")
                print(str(income_data))

                # Put the data in a DataFrame
                income_df = pd.DataFrame(income_data_parsed)

                print(" ================== TESTING ===================== ")
                print(income_df)

                # Display
                #print('-'*100)
                #print('Before Reindexing')
                #print('-'*100)
                #print(f"{income_df.head()}")

                # Define the Index column, rename it, and we need to make sure to drop the old column once we reindex.
                income_df.index = income_df[0]
                income_df.index.name = 'Category'
                income_df = income_df.drop(0, axis = 1)

                # Display
                print('-'*100)
                print('Before Regex')
                print('-'*100)
                print(f"{income_df.head()}")

                income_df = income_df.replace('[\$,)]','', regex=True )
                income_df = income_df.replace('[(]','-', regex=True)
               # income_df = income_df.replace('[]0-9[]', '', regex=True)
                income_df = income_df.replace('', 'NaN', regex=True)
                income_df = income_df.replace('[1]', 'NaN', regex=False)
                income_df = income_df.replace('[2]', 'NaN', regex=False)
                income_df = income_df.replace('[3]', 'NaN', regex=False)
                income_df = income_df.replace('[4]', 'NaN', regex=False)
                income_df = income_df.replace('[5]', 'NaN', regex=False)
                income_df = income_df.replace('[6]', 'NaN', regex=False)
                income_df = income_df.replace('[7]', 'NaN', regex=False)
                income_df = income_df.replace('[8]', 'NaN', regex=False)
                income_df = income_df.replace('[9]', 'NaN', regex=False)
                
                # Display
                print('-'*100)
                print('Before type conversion')
                print('-'*100)
                print(f"{income_df.head()}")

                #print(" ")
                #print(" ")
                #print(" ================== income_df ===================== ")
                #print(f"{income_df}")

                income_df = income_df.loc[:, ~income_df.apply(lambda x: x.nunique() == 1 and x[0]=='NaN', axis=0)]
                print(" ================== testyyy ===================== ")
                print(income_df)

                # everything is a string, so let's convert all the data to a float.
                income_df = income_df.astype(float)

                # Change the column headers
                income_df.columns = income_header

                # Display
                print('-'*100)
                print('Final Product')
                print('-'*100)

                # show the dataframe
                display(income_df)

                # drop the data in a CSV file if need be.
                income_df.to_csv('Apps/Collection/src/resources/test-income-state.csv')


                
                

                    