#!/usr/bin/python

import pywikibot
import re
from datetime import date
import datetime

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
version = '0.1.0'
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
    global dates
    global nonDate
    global entries
    global problem
    templateLink = title.lstrip('{').rstrip('}')
    if 'Template:' not in templateLink:
        templateLink = 'Template:'+templateLink
    page = pywikibot.Page(site,templateLink)
    if 'Please do not modify this page.' in page.text:
        entries.pop()
    elif '[[File:Symbol confirmed.svg|16px]]' in page.text \
    or '[[File:Symbol voting keep.svg|16px]]' in page.text:
        dates[i][1].append('{{'+templateLink+'}}')
        nonDate.append('{{'+templateLink+'}}')
        entries.pop()
        
site = pywikibot.Site('en', 'wikipedia')
nomPage      = pywikibot.Page(site,'Template talk:Did you know')
approvedPage = pywikibot.Page(site,'Template talk:Did you know/Approved')

dateRegex = re.compile(r'on (.*?) (\d+)=')

DYKpage = nomPage.text.split('\n')
dates   = []
nonDate = []
entries = []
problem = []

i=-1
for line in DYKpage:
    entries.append(line)
    if '==Articles' in line:
        matches=dateRegex.search(line)
        month = monthConvert(matches.group(1))
        day = int(matches.group(2))
        date = datetime.date(month=month,day=day,year=2016)
        section = line
        i+=1
        dates.append([date,[section]])
    elif 'Did you know nominations/' in line and '<!--' not in line:
        if '}}{{' in line:
            splitLine = line.split('}}{{')
            for title in splitLine:
                try:
                    checkPage(title)
                except Exception as e:
                    print(e)
                    problem.append([i+1,line,e])
                    continue
        else:
            line = line.split('}')[0]
            try:
                checkPage(line)
            except Exception as e:
                print(e)
                problem.append([i+1,line,e])
                continue
                
toPrint=[]
dates.sort(key=lambda x: x[0])
for entry in dates:
    if len(entry[1]) > 1:
        toPrint+=entry[1]
        
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
approvedText[0]+=toPrint
approvedText[1].append('\n'.join(nonDate))
for line in approvedPage.text.split('\n'):
    if '==Special occasion holding area==' in line:
        passed = 1
        approvedText[0].append(line+'\n')
        approvedText[1].append(line+'\n')
    elif passed == 1:
        approvedText[0].append(line+'\n')
        approvedText[1].append(line+'\n')
        
# Determine if the bot should write to a live page or the test page. Defaults to 
#     test page. Value of -1 tests backlog update (not standard because the file
#     size is very big).
if live == False:
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
