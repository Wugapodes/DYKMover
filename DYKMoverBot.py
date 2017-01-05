#!/usr/bin/python

import pywikibot
import re
from datetime import date
import datetime
import logging
import sys

########
# Changing this to 1 makes your changes live on the report page, do not set to
# live mode unless you have been approved for bot usage. Do not merge commits 
# where this is not default to 0
########
live = 0
########
# Style: 0 = with date sectionsl 1 = without
########
style = 0
########
# Version Number
########
version = '0.4.5'
########

'''
Copyright (c) 2016 Wugpodes

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to do 
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
THE SOFTWARE.
'''

def monthConvert(name):
    '''
    Takes in either the name of the month or the number of the month and returns
    the opposite. An input of str(July) would return int(7) while an input of
    int(6) would return str(June).
    Takes:   int OR string
    Returns: string OR int
    '''
    if type(name) is str:
        if name == "January": return 1
        elif name == "February": return 2
        elif name == "March": return 3
        elif name == "April": return 4
        elif name == "May": return 5
        elif name == "June": return 6
        elif name == "July": return 7
        elif name == "August": return 8
        elif name == "September": return 9
        elif name == "October": return 10
        elif name == "November": return 11
        elif name == "December": return 12
        else: raise ValueError
    elif type(name) is int:
        if name == 1:return('January')
        elif name == 2:return('February')
        elif name == 3:return('March')
        elif name == 4:return('April')
        elif name == 5:return('May')
        elif name == 6:return('June')
        elif name == 7:return('July')
        elif name == 8:return('August')
        elif name == 9:return('September')
        elif name == 10:return('October')
        elif name == 11: return('November')
        elif name == 12: return('December')
        else: raise ValueError
            
def checkPage(title):
    '''
    Takes the title of a DYK nom page and loads the wikitext. Looks for a DYK
    tick that shows it was approved or approved (AGF). If so it adds it to 
    various lists so that it can be added to the approved page.
    Returns None, implicitly 
    '''
    global dates
    global nonDate
    global entries
    global problem
    title = title.lstrip('{').rstrip('}')
    approved = computeNomStatus(title)
    if approved == -1:
        entries.pop()
    elif approved == 1:
        dates[-1][1].append('{{'+title+'}}')
        nonDate.append('{{'+title+'}}')
        entries.pop()
    else:
        pass
            
def computeNomStatus(link,status=0):
    link = link.lstrip('{').rstrip('}')
    if 'Template:' not in link:
        link = 'Template:'+link
    page = pywikibot.Page(site,link)
    if 'Please do not modify this page.' in page.text:
        status=-1
    else:
        for line in page.text.split('\n'):
            if '[[File:Symbol confirmed.svg|16px]]' in line \
            or '[[File:Symbol voting keep.svg|16px]]' in line:
                status = 1
            elif '[[File:Symbol question.svg|16px]]' in line \
            or '[[File:Symbol possible vote.svg|16px]]' in line \
            or '[[File:Symbol delete vote.svg|16px]]' in line \
            or '[[File:Symbol redirect vote 4.svg|16px]]' in line:
                status = 0
    return(status)

def mergeNominations(item = ''):
    '''
    Takes an index for the list dates and appends the entries in that section
    to the proper section on the approved page. Returns None, implicitly
    '''
    global approvedPageDates
    global dates
    if item == '':
        pass
    else:
        for entry in approvedPageDates:
            if dates[item][0] in entry:
                entry[1]+=dates[item][1][1:]
                
def computeYear(oMonth):
    '''
    Gives correct year over one year change, ie, for 11 months. Sections older
    than 11 months will not yield the correct results
    '''
    now = datetime.datetime.now()
    cMonth = now.month
    cYear = now.year
    if oMonth <= cMonth:
        year = cYear
    else:
        year = cYear - 1
    return(year)
    
def startLogging(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), None)
    if numeric_level != None:
        logging.basicConfig(
            level=numeric_level,
            filename='Testing.log',
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %I:%M:%S %p'
        )
    else:
        logging.basicConfig(
            level=logging.WARNING,
            filename='./log/DYKMoverBot.log',
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %I:%M:%S %p'
        )
        logging.warning('Invalid log level \'%s\'. ' \
                       +'Defaulting to WARNING' % loglevel)
        
def checkArgs(arg):
    arg = arg.split('=')
    if arg[0] == '--log' or arg[0] == '-l':
        startLogging(arg[1])
    else:
        raise ValueError('Unknown command line argument \'%s\'' % arg[0])

# Start log
#for i in range(1,len(sys.argv)):
#    checkArgs(sys.argv[i])

logging.info("### Starting new run ###")
logging.info("live is set to %s" % live)
logging.info("style is set to %s" % style)
logging.info("DYKMoverBot version %s" % version)

# Load the various pages
logging.info("Loading pages")
site = pywikibot.Site('en', 'wikipedia')
nomPage      = pywikibot.Page(site,'Template talk:Did you know')
#approvedPage = pywikibot.Page(site,'Template talk:Did you know/Approved')
approvedPage = pywikibot.Page(site,'User:Wugapodes/DYKTest/0')
approvedPage1= pywikibot.Page(site,'User:Wugapodes/DYKTest/1')

dateRegex = re.compile(r'on (.*?) (\d+)=')

DYKpage = nomPage.text.split('\n')
dates   = []
nonDate = []
entries = []
problem = []

# Get approved nominations on the DYK page
logging.info("Reading Nomination page")
for line in DYKpage:
    entries.append(line)
    if '==Articles' in line:
        matches=dateRegex.search(line)
        month = monthConvert(str(matches.group(1)))
        day = int(matches.group(2))
        dt = datetime.date(month=month,day=day,year=computeYear(month))
        section = line
        dates.append([dt,[section]])
    elif 'Did you know nominations/' in line and '<!--' not in line:
        if '}}{{' in line:
            logging.debug("Multiple nominations on one line.\n"\
                         +"Section: %s" % line)
            splitLine = line.split('}}{{')
            for title in splitLine:
                try:
                    checkPage(title)
                except Exception as e:
                    logging.error(
                        "Function checkPage did not complete successfully.\n"\
                        +str(e)+"\n"+title
                    )
                    logging.debug(line)
                    print(e)
                    problem.append([line,e])
                    continue
        else:
            line = line.split('}')[0]
            try:
                checkPage(line)
            except Exception as e:
                logging.error(
                    "Function checkPage did not complete successfully.\n"\
                    +str(e)+"\n"+line
                )
                print(e)
                problem.append([line,e])
                continue

# Get the text on the approved page and then update the proper sections
# with entries newly approved
logging.info("Reading Approved page")
approvedPageText = approvedPage.text.split('\n')
sectionName = ''
approvedPageDates = []
oldLine = ''
datesToRemove = []
if style != 1:
    logging.info("Starting style 0 parsing")
    for line in approvedPageText:
        if '==Articles' in line:
            mergeNominations(oldLine)
            matches=dateRegex.search(line)
            month = monthConvert(str(matches.group(1)))
            day = int(matches.group(2))
            dt = datetime.date(month=month,day=day,year=computeYear(month))
            sectionName = line
            for item in dates:
                if dt in item:
                    oldLine = dates.index(item)
                    datesToRemove.append(oldLine)
                    break
                else:
                    continue
            approvedPageDates.append([dt,[sectionName]])
        elif 'Did you know nominations/' in line and '<!--' not in line:
            if '}}{{' in line:
                splitLine = line.split('}}{{')
                for title in splitLine:
                    if computeNomStatus(title) >= 0:
                        try:
                            approvedPageDates[-1][1].append('{{'+title+'}}')
                        except Exception as e:
                            logging.warning("The approved page is empty?\n"+str(e))
            else:
                line = line.split('}')[0]
                if computeNomStatus(title) >= 0:
                    try:
                        approvedPageDates[-1][1].append('{{'+title+'}}')
                    except Exception as e:
                        logging.warning("The approved page is empty?\n"+str(e))
    dates2 = []
    for i in datesToRemove:
        dates2.append(dates[i])
        

    newSections = [x for x in dates if x not in dates2 and len(x[1]) > 1]
    approvedPageDates+=newSections
    toPrint=[]
    approvedPageDates.sort(key=lambda x: x[0])
    for entry in dates:
        if len(entry[1]) > 1:
            toPrint+=entry[1]
 

           
approvedPage1Text = approvedPage1.text.split('\n')
toRemoveFromNonDate = []
if style != 0:
    logging.info("Starting style 1 parsing.")
    logging.warning("Style 1 is no longer maintained. "\
        +"Bot may behave incorrectly or not at all.")
    for line in approvedPage1Text:
        if line in nonDate:
            toRemoveFromNonDate.append(line)
    nonDateTemp = [x for x in nonDate if x not in toRemoveFromNonDate]
    nonDate = nonDateTemp

        
# Create the page text to be output
logging.info("Creating output text")
approvedText2 = approvedPage1.text.split('\n')
passed = 0
approvedText = [
        [
        "{{/top}}\n",
        "=Nominations=\n",
        "==Approved nominations==\n",
        "<!-- This section will hold approved nominations, with the templates "\
        +"transcluded in the same manner as the regular nominations page. "\
        +"While the exact format of the section has not yet been decided-while"\
        +" it seems unlikely that it will be by date, it may be divided into "\
        +"other sections-it is likely that the oldest approvals will go at the"\
        +" top and the most recent ones at the bottom of each section. -->\n"
        ],
        [
        "{{/top}}\n",
        "=Nominations=\n",
        "==Approved nominations==\n",
        "<!-- This section will hold approved nominations, with the templates "\
        +"transcluded in the same manner as the regular nominations page. "\
        +"While the exact format of the section has not yet been decided-while"\
        +" it seems unlikely that it will be by date, it may be divided into "\
        +"other sections-it is likely that the oldest approvals will go at the"\
        +" top and the most recent ones at the bottom of each section. -->\n"
        ]
    ]

for line in approvedText2:
    if '==Approved nominations==' in line:
        passed=1
    elif '==Special occasion holding area==' in line:
        passed=2
        approvedText[1].append('\n'.join(nonDate))
        approvedText[1].append('\n'+line+'\n')
    elif passed > 0:
        approvedText[1].append(line+'\n')
approvedText[0].append('\n'.join(toPrint))
for line in approvedPage.text.split('\n'):
    if '==Special occasion holding area==' in line:
        passed = 1
        approvedText[0].append('\n'+line+'\n')
    elif passed == 1:
        approvedText[0].append(line+'\n')
    
print('Done')

approvedText = [
        [
        "{{/top}}\n",
        "=Nominations=\n",
        "==Approved nominations==\n",
        "<!-- This section will hold approved nominations, with the templates "\
        +"transcluded in the same manner as the regular nominations page. "\
        +"While the exact format of the section has not yet been decided-while"\
        +" it seems unlikely that it will be by date, it may be divided into "\
        +"other sections-it is likely that the oldest approvals will go at the"\
        +" top and the most recent ones at the bottom of each section. -->\n"
        ],
        [
        "{{/top}}\n",
        "=Nominations=\n",
        "==Approved nominations==\n",
        "<!-- This section will hold approved nominations, with the templates "\
        +"transcluded in the same manner as the regular nominations page. "\
        +"While the exact format of the section has not yet been decided-while"\
        +" it seems unlikely that it will be by date, it may be divided into "\
        +"other sections-it is likely that the oldest approvals will go at the"\
        +" top and the most recent ones at the bottom of each section. -->\n"
        ]
    ]
        
# Determine if the bot should write to a live page or the test page. Defaults to 
#     test page. Value of -1 tests backlog update (not standard because the file
#     size is very big).
if type(live) is str:
    pass
    page = pywikibot.Page(site,'Template talk:Did you know/Approved')
    page.text=''.join(approvedText[style])
    page.save('moving '+str(len(nonDate))+'tentatively approved nominations '\
              +'from [[WP:DYKN]], WugBot v'+version)
    page = pywikibot.Page(site,'Template talk:Did you know')
    # This is where the rest of the live stuff will go once I figure out
    #   how the other bots handle empty sections
else:
    page = pywikibot.Page(site,'User:Wugapodes/DYKTest/0')
    page.text=''.join(approvedText[0])
    page.save('test of DYKMover, WugBot v'+version+' section style')
    page = pywikibot.Page(site,'User:Wugapodes/DYKTest/1')
    page.text=''.join(approvedText[1])
    page.save('test of DYKMover, WugBot v'+version+' nosection style')
    page = pywikibot.Page(site,'User:Wugapodes/DYKTest/0')
    
print('Done')
