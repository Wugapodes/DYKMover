#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import timeit

import logging
import pywikibot
import datetime

########
# Changing this to 1 makes your changes live on the report page, do not set to
# live mode unless you have been approved for bot usage. Do not merge commits 
# where this is not default to 0
########
live = 0
########
# Version Number
########
version = '0.11.0-dev'
########

class DateHeading():
    def __init__(self,section,site):
        self.month   = monthConvert(section[0])
        self.day     = int(section[1])
        self.year    = self.computeYear()
        self.date    = datetime.date(month=self.month,day=self.day,year=self.year)
        rawEntry     = section[2]
        self.entries = []
        entryRegEx   = re.compile(
                    r'{{(.*?)}}'
                    )
        entryOut     = entryRegEx.findall(rawEntry)
        for entry in entryOut:
            self.entries.append(Entry(entry,site))
        
    def computeYear(self):
        '''
        Gives correct year over one year change, ie, for 11 months. Sections older
        than 11 months will not yield the correct results
        '''
        now = datetime.datetime.now()
        cMonth = now.month
        cYear = now.year
        if self.month <= cMonth:
            year = cYear
        else:
            year = cYear - 1
        return(year)
        
    def setEntries(self,ent):
        self.entries = ent
        
    def printSection(self,comment=''):
        if len(self.entries) < 1:
            return('')
        if len(comment) > 0:
            comment = '<!-- %s -->\n'%comment
        else:
            comment = ''
        header = '\n===Articles created/expanded on %s %d===\n%s'%(monthConvert(self.month),self.day,comment)
        fmtdEntries = ['{{'+x+'}}' for x in [y.title for y in self.entries]]
        entries = '\n'.join(fmtdEntries)
        return(header+entries)


class Entry():
    def __init__(self,title,site):
        pyWikiSite = site
        self.title = title
        self.dykcr = re.compile(r'status\s*=\s*(?:y|Y)')
        self.approved = False
        self.closed   = False
        self.setApproval(pyWikiSite)
        
    def setApproval(self,pyWikiSite):
        link = self.title
        link = link.replace('_',' ')
        if 'Template:' not in link:
            link = 'Template:'+link
        entryPage = pywikibot.Page(pyWikiSite,link)
        if 'Please do not modify this page.' in entryPage.text:
            self.closed = True
        else:
            dykchecklist = []
            dykc = 0
            for line in entryPage.text.split('\n'):
                if dykc == 1:
                    dykchecklist.append(line)
                    if '}}' in line:
                        dykc=0
                        self.approved = self.computeDYKChecklistStatus('\n'.join(dykchecklist))
                elif '{{DYK checklist' in line:
                    if '}}' in line:
                        self.approved = self.computeDYKChecklistStatus(line)
                    else:
                        dykchecklist.append(line)
                        dykc = 1
                if '[[File:Symbol confirmed.svg|16px]]' in line \
                or '[[File:Symbol voting keep.svg|16px]]' in line:
                    self.approved = True
                elif '[[File:Symbol question.svg|16px]]' in line \
                or '[[File:Symbol possible vote.svg|16px]]' in line \
                or '[[File:Symbol delete vote.svg|16px]]' in line \
                or '[[File:Symbol redirect vote 4.svg|16px]]' in line:
                    self.approved = False
                    
    def getApprovalStatus(self):
        return(self.approved)
        
    def getClosedStatus(self):
        return(self.closed)
    
    def computeDYKChecklistStatus(self,template):
        if type(template) is list:
            template='\n'.join(template)
        elif type(template) is not str and type(template) is not unicode:
            raise ValueError('template must be either list or string')
        match = re.search(self.dykcr,template)
        if match != None:
            return(True)
        else:
            return(False)


def monthConvert(name):
    '''
    Takes in either the name of the month or the number of the month and returns
    the opposite. An input of str(July) would return int(7) while an input of
    int(6) would return str(June).
    Takes:   int OR string
    Returns: string OR int
    '''
    try:
        name = int(name)
    except ValueError:
        name = str(name)
    if type(name) is str:
        name
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
        
def printPage(sectionList,nomPage=False,apText=None):
    pageOutput = ''
    if nomPage:
        head = '{{Template talk:Did you know/Header}}\n\n'\
        +'=Nominations=\n==Older nominations==\n\n'
        pageOutput += head
        for section in sectionList:
            pageOutput += section.printSection(
                comment='After you have created your nomination page, please '\
                        +'add it (e.g., {{Did you know nominations/YOUR '\
                        +'ARTICLE TITLE}}) to the TOP of this section (after '\
                        +'this comment).'
            )
            pageOutput += '\n'
        foot = "==Special occasion holding area==\n'''The holding area has "\
               +"moved''' to its new location at the bottom of the [[Template "\
               +"talk:Did you know/Approved#Special occasion holding "\
               +"area|Approved page]]. Please only place approved templates "\
               +"there; do not place them below.\n"\
               +"\n"\
               +":''Do '''not''' nominate articles in this section&mdash;nominate "\
               +"all articles in the [[Template talk:Did you "\
               +"know#Nominations|nominations]] section above, under the date "\
               +"on which the [[WP:DYKTN#article|article]] was created or "\
               +"moved to mainspace, or the [[WP:DYKTN#expansion|expansion]] "\
               +"began; indicate in the nomination any request for a "\
               +"specially timed appearance on the main page.''\n"\
               +":''Note: Articles nominated for a special occasion should be "\
               +"nominated (i) within seven days of creation or expansion "\
               +"(as usual) and (ii) between five days and six weeks before "\
               +"the occasion, to give reviewers time to check the "\
               +"nomination. April Fools' Day is an exception to these "\
               +"requirements; see '''[[Wikipedia:April Fool's Main Page/Did "\
               +"You Know]]'''.''\n"\
               +"\n"\
               +"[[Category:Wikipedia Did you know]]\n"\
               +"[Category:Main Page discussions]]"
        pageOutput += foot
        return(pageOutput)
    elif not nomPage:
        if not apText:
            raise ValueError('Printing Approved Page Requires approved page text')
            return(None)
        head = "{{/top}}\n"\
               +"=Nominations=\n"\
               +"==Approved nominations==\n"\
               +"<!-- This section will hold approved nominations, with the "\
               +"templates transcluded in the same manner as the regular "\
               +"nominations page. While the exact format of the section has "\
               +"not yet been decided-while it seems unlikely that it will be "\
               +"by date, it may be divided into other sections-it is likely "\
               +"that the oldest approvals will go at the top and the most "\
               +"recent ones at the bottom of each section. -->\n"
        pageOutput += head
        for section in sectionList:
            pageOutput += section.printSection()
            pageOutput += '\n'
        holdingArea = re.search('(==Special occasion (?:.|\s)*]])',apText).group(0)
        pageOutput+=holdingArea
        return(pageOutput)
        
def writePage(sectionList,site,write,nomPage=False,apText=None):
    text = printPage(sectionList,nomPage,apText)
    if not text:
        return(None)
    if not nomPage:
        write = write+'/Approved'
    page = pywikibot.Page(site,write)
    page.text = text
    page.save('EditSummary')
        
def main():
    global live
    #logging.info("Loading pages")
    site    = pywikibot.Site('en', 'wikipedia')

    #logging.info("### Starting new run ###")
    #logging.info("live is set to %s" % live)
    #logging.info("style is set to %s" % style)
    #logging.info("DYKMoverBot version %s" % version)
    
    if live == -1:
        read  = 'User:Wugapodes/DYKTest'
        write = 'User:Wugapodes/DYKTest'
    elif live == 0:
        read  = 'Template talk:Did you know'
        write = 'User:Wugapodes/DYKTest'
    elif live == 1:
        read  = 'Template talk:Did you know'
        write = 'Template talk:Did you know'

    nomPage = pywikibot.Page(site,read)
    approvedPage = pywikibot.Page(site,read+'/Approved')

    sectionRegEx = re.compile(
                        r'===.*? on (.*?) (\d+)===\n(?:|<!--.*?-->)(?:|\n+)({{(?:.*\n)+?)(?===)'
                        )

    nomPageText = nomPage.text
    nomPageSections = []
    for section in sectionRegEx.findall(nomPageText):
        nomPageSections.append(DateHeading(section,site))

    approvedPageText = approvedPage.text
    approvedPageSection = {}
    for section in sectionRegEx.findall(approvedPageText):
        sect = DateHeading(section,site)
        if sect.month not in approvedPageSection:
            approvedPageSection[sect.month] = {}
        if sect.day not in approvedPageSection[sect.month]:
            approvedPageSection[sect.month][sect.day] = sect
        
    for section in nomPageSections:
        toApproved = [entry for entry in section.entries if entry.approved]
        stayOnNom  = [entry for entry in section.entries if not entry.approved]
        
        day = section.day
        month = section.month
        
        if month not in approvedPageSection:
            approvedPageSection[month] = {}
        if day not in approvedPageSection[month]:
            approvedPageSection[month][day] = section
            approvedPageSection[month][day].setEntries(toApproved)
        else:
            approvedEntries = approvedPageSection[month][day].entries + toApproved
            approvedPageSection[month][day].setEntries(approvedEntries)
            
    nomPageSections.sort(key=lambda x:x.date)
    approvedSectionList = [approvedPageSection[m][d] for m in approvedPageSection.keys() for d in approvedPageSection[m].keys()]
    approvedSectionList.sort(key=lambda x:x.date)

	nom_req_start = timeit.default_timer()
    nomPageCheck = pywikibot.Page(site,read)
    nom_req_end = timeit.default_timer()
    if nomPageCheck.text != nomPage.text:
        return(False)
    writePage(nomPageSections,site,write,True)
    nom_write_end = timeit.default_timer()
    
    app_req_start = timeit.default_timer()
    approvedPageCheck = pywikibot.Page(site,read+'/Approved')
    app_req_end = timeit.default_timer()
    if approvedPageCheck.text != approvedPage.text:
        return(False)
    writePage(approvedSectionList,site,write,apText=approvedPage.text)
    app_write_end = timeit.default_timer()
    
    nom_req_time = nom_req_end - nom_req_start
    app_req_time = app_req_end - nom_req_start
    nom_write_time = nom_write_end - nom_req_start
    app_write_time = app_write_end - app_req_start
    times = [nom_req_time,nom_write_time,app_req_time,app_write_time]
    times = [str(x) for x in times]
    
    with open('TimingData.csv','a') as f:
    	f.write(','.join(times))
    
main()
