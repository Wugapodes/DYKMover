#!/usr/bin/python
# -*- coding: UTF-8 -*-

__version__ = '0.11.1-dev'

import re
import os
import codecs
import timeit
from copy import copy

import logging
import pywikibot
import datetime

"""
CONFIGURATION VARIABLES

The following variables toggle the way the bot interacts with pages and their
    setting should reflect consensus.
ATTRIBUTE   VALUES  DESCRIPTION
live        -1      Debug mode. Only reads from test pages. Does not write to
                      Wikipedia at all, just computes and exits.
             0      Testing mode. Reads from the live DYKN pages. Writes to
                      test pages only.
             1      Live mode. The bot is live and edits outside Userspace.
                      This mode should not be used without approval from the
                      Bot Approval Group on the English Wikipedia.

two_way      True   Nominations are moved to and from the approval page as their
                      approval changes.
             False  Once a nomination is moved to the approved page, it is not
                      moved back by the bot.
rm_closed    True   Closed nominations are removed from pages automatically by
                      the bot.
             False  Closed nominations are not removed by the bot and must be
                      removed by a human.
"""
live = -1
two_way = True
rm_closed = True

"""
Global regular expressions
"""
old_nom_regex = re.compile(
    r'==Older nominations==\n((.*\n)*)==Current nominations'
    )
current_regex = re.compile(
    r'==Current nominations.*?==\n((.*\n)*)==Special'
    )
section_regex = re.compile(
    r'===.*? on (.*?) (\d+)===\n(?:|<!--.*?-->)(?:|\n+)({{(?:.*\n?)+?)(?===|$)'
    )

"""
Pywikibot configuration
"""
site = pywikibot.Site('en', 'wikipedia')

class DateHeading():
    def __init__(self,section,**kwargs):
        old = kwargs['old']
        page = kwargs['page']
        self.old = old
        self.page = page
        self.entries = []
        if 'Approved nominations' == page:
            page = 'apr'
        else:
            page = 'nom'
        if section == None:
            self.month = kwargs['month']
            self.day = kwargs['day']
            self.year = kwargs['year']
            self.date = kwargs['date']
            self.entries = kwargs['entries']
            try:
                self.title = kwargs['title']
            except:
                print(self.month,self.day,"No title?")
        else:
            self.month   = self.monthConvert(section[0])
            self.day     = int(section[1])
            self.year    = self.computeYear()
            self.date    = datetime.date(month=self.month,day=self.day,year=self.year)
            rawEntry     = section[2]
            try:
                self.title = str(self.day)+' '+self.monthConvert(self.month)
            except:
                print(section)
            entryRegEx   = re.compile(
                        r'{{(.*?)}}'
                        )
            entryOut     = entryRegEx.findall(rawEntry)
            for entry in entryOut:
                self.entries.append(Entry(entry))

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

    def printSection(self,apr=False,comment=''):
        global rm_closed

        print(apr)
        if rm_closed:
            if apr:
                toPrint = [x for x in self.entries if x.approved and not x.closed]
            else:
                toPrint = [x for x in self.entries if not x.approved and not x.closed]
        else:
            if apr:
                toPrint = [x for x in self.entries if x.approved]
            else:
                toPrint = [x for x in self.entries if not x.approved]
        print(self.title,toPrint)
        if len(comment) > 0:
            comment = '<!-- %s-->\n'%comment
        else:
            comment = ''
        header = '\n===Articles created/expanded on %s %d===\n%s'%(self.monthConvert(self.month),self.day,comment)
        fmtdEntries = ['{{'+x+'}}' for x in [y.title for y in self.entries]]
        entries = '\n'.join(fmtdEntries)
        return(header+entries)

    def monthConvert(self,name):
        '''
        Takes in either the name of the month or the number of the month and
        returns the opposite. An input of str(July) would return int(7) while
        an input of int(6) would return str(June).

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

    def __str__(self):
        global rm_closed
        lines = []
        month = self.monthConvert(self.month)
        day = str(self.day)
        h_date = month+' '+day
        if self.page == 'nom':
            comment = '\n<!-- After you have created your nomination page, '\
                     +'please add it (e.g., {{Did you know nominations/YOUR '\
                     +'ARTICLE TITLE}}) to the TOP of this section (after '\
                     +'this comment).-->'
        else:
            comment = ''
        header = '\n===Articles created/expanded on '+h_date+'==='+comment
        lines.append(header)
        if rm_closed:
            lines = lines + [str(x) for x in self.entries if not x.closed]
        else:
            lines = lines + [str(x) for x in self.entries]
        out = '\n'.join(lines)
        return(out)

    def __dict__(self):
        output = {}
        output['month'] = self.month
        output['day'] = self.day
        output['year'] = self.year
        output['date'] = self.date
        output['entries'] = self.entries
        output['title'] = self.title
        output['old'] = self.old
        output['page'] = self.page
        return(output)

    def __len__(self):
        return(len(self.entries))

class Entry():
    def __init__(self,title):
        self.title = title
        self.approved = False
        self.closed   = False
        self.setApproval()

    def setApproval(self):
        global site
        global two_way

        link = self.title
        link = link.replace('_',' ')
        if 'Template:' not in link:
            link = 'Template:'+link
        entryPage = pywikibot.Page(site,link)
        if 'Please do not modify this page.' in entryPage.text:
            self.closed = True
            return()
        dykchecklist = []
        dykc = 0
        for line in entryPage.text.split('\n'):
            if '{{DYK checklist' in line:
                if '}}' in line:
                    self.approved = self.computeDYKChecklistStatus(line)
                else:
                    dykchecklist.append(line)
                    dykc = 1
            elif dykc == 1:
                dykchecklist.append(line)
                if '}}' in line:
                    dykc=0
                    self.approved = self.computeDYKChecklistStatus('\n'.join(dykchecklist))
            if '[[File:Symbol confirmed.svg|16px]]' in line \
            or '[[File:Symbol voting keep.svg|16px]]' in line:
                self.approved = True
                if two_way != True:
                    break
                else:
                    continue
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
        dykcr = re.compile(r'status\s*=\s*(?:y|Y)')
        match = re.search(dykcr,template)
        if match != None:
            return(True)
        else:
            return(False)

    def info(self):
        if self.approved:
            a = 'Approved'
        else:
            a = 'Not approved'
        if self.closed:
            c = 'Closed'
        else:
            c = 'Not closed'
        value = a + ' and ' + c
        return(value)

    def __str__(self):
        string = '{{Template:'+self.title+'}}'
        return(string)

class PageSection():
    def __init__(self,title,old,text):
        self.title = title
        self.old = old
        self.entries = []
        self.set_groups(text,old)

    def set_groups(self,text,old):
        global section_regex
        entries = self.entries
        for section in section_regex.findall(text):
            entries.append(DateHeading(section,old=old,page=self.title))
        self.entries = entries

    def _move(self,t_page,section,nom):
        for s in t_page.entries:
            if s.date == section.date:
                s.entries.append(nom)
                section.entries.remove(nom)
                break
        section_copy = section.__dict__
        section_copy['entries'] = [nom]
        t_page.entries.append(DateHeading(None,**section_copy))

    def __str__(self):
        lines = []
        lines.append('=='+title+'==')
        lines.append('<!-- automatically moved by bot -->')
        lines = lines + [str(x) for x in self.entries]
        out = '\n'.join(lines)
        return(out)


class NomPageSection(PageSection):
    def __init__(self,*args):
        PageSection.__init__(self,*args)
        self.approved_num = None
        self.closed_num = None

    def move_entries(self,apr_page):
        num = 0
        closed = 0
        for section in self.entries:
            for nom in section.entries:
                if nom.closed:
                    closed += 1
                if nom.approved:
                    num += 1
                    PageSection._move(self,apr_page,section,nom)
        self.approved_num = num
        self.closed_num = closed


class AprPageSection(PageSection):
    def __init__(self,*args):
        PageSection.__init__(self,*args)
        self.unapproved_num = None
        self.closed_num = None

    def move_entries(self,cur,old):
        unapr = 0
        closed = 0
        for section in self.entries:
            for nom in section.entries:
                if nom.closed:
                    closed += 1
                elif not nom.approved:
                    unapr += 1
                    if section.date in cur.entries:
                        nom_page = cur
                    else:
                        nom_pge = old
                    PageSection._move(nom_page,section,nom)
        self.unapproved_num = unapr
        self.closed_num = closed


def write_error(func_msg=None, cause_msg=None):
    msg_template = "== WugBot Error ==\n"+\
    "On "+str(datetime.date.today())+" at "+\
    str(datetime.datetime.utcnow().time()).split('.')[0]+" UTC WugBot "+\
    "encountered "+func_msg+"\n\n"+\
    "The error seems to have "+cause_msg+"\n"+\
    "{{ping|Wugapodes}} ~~~~"

def writePages(read,write,n_text,a_text,checks,msgs):
    global site
    global live
    nom_check = checks[0]
    apr_check = checks[1]
    na_msg = msgs['a']+'[[/Approved|approved page]]. '
    nt_msg = msgs['t']+' removed.'
    aa_msg = msgs['a']+'approved page. '
    at_msg = msgs['t']+'[[WP:DYKN|removed]]. '
    c_msg = msgs['c']
    v_msg = msgs['v']
    n_summary = na_msg+nt_msg+c_msg+v_msg
    a_summary = aa_msg+at_msg+c_msg+v_msg

    req_start = timeit.default_timer()
    n_page = pywikibot.Page(site,write)
    a_page = pywikibot.Page(site,write+'/Approved')
    req_end = timeit.default_timer()
    if a_page.text != apr_check or n_page.text != nom_check:
        write_end = timeit.default_timer()
        success = False
        if live != 0:
            return(success,(req_start,req_end,write_end))
    n_page.text = n_text
    a_page.text = a_text
    if live <= -1:
        print('Not writing, live = %s'%live)
    else:
        n_page.save(n_summary)
        a_page.save(a_summary)
    write_end = timeit.default_timer()
    success = True
    return(success,(req_start,req_end,write_end))

def main():
    global site
    global live
    global two_way
    global rm_closed
    global old_nom_regex
    global current_regex
    global section_regex
    #logging.info("Loading pages")
    #logging.info("### Starting new run ###")
    #logging.info("live is set to %s" % live)
    #logging.info("style is set to %s" % style)
    #logging.info("DYKMoverBot version %s" % version)

    if live <= -1:
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

    # Parse the nom page old and current sections.
    nomPageText = nomPage.text
    o_text = old_nom_regex.search(nomPageText).group(1)
    c_text = current_regex.search(nomPageText).group(1)
    oldNoms = NomPageSection('Older nominations',True,o_text)
    curNoms = NomPageSection('Current nominations',False,c_text)

    approvedPageText = approvedPage.text
    aprNoms = NomPageSection('Approved nominations',False,approvedPageText)

    oldNoms.move_entries(aprNoms)
    curNoms.move_entries(aprNoms)
    aprNoms.move_entries(oldNoms,curNoms)

    approved_num = oldNoms.approved_num + curNoms.approved_num
    unapproved_num = aprNoms.unapproved_num
    closed_num = oldNoms.closed_num + curNoms.closed_num + aprNoms.closed_num

    a_msg = str(approved_num)+' approved nominations moved to the '
    if closed_num > 0:
        if rm_closed:
            c_msg = str(closed_num)+' closed nominations removed. '
        else:
            c_msg = str(closed_num)+' closed nominations not removed. '
    else:
        c_msg=''
    if unapproved_num > 0:
        if two_way:
            t_msg = str(unapproved_num)+' unapproved nominations '
        else:
            t_msg = str(unapproved_num)+' unapproved nominations not '
    else:
        t_msg = ''
    v_msg = 'WugBot v'+__version__

    curNoms.entries.sort(key=lambda x:x.date)
    oldNoms.entries.sort(key=lambda x:x.date)
    aprNoms.entries.sort(key=lambda x:x.date)

    nomPageLines = nomPageText.split('\n')
    header = []
    end = []
    for line in nomPageLines:
        header.append(line)
        if '=Nominations=' in line:
            break
    for i in range(len(nomPageLines)):
        end.append(line)
        if '==Special occasion holding area==' in nomPageLines[-i]:
            break
    end.reverse()
    head = '\n'.join(header)
    tail = '\n'.join(end)

    new_nom_page_list = [head,str(oldNoms),str(curNoms),tail]
    new_nom_page = '\n'.join(new_nom_page_list)

    aprPageLines = approvedPageText.split('\n')
    header = []
    end = []
    for line in aprPageLines:
        header.append(line)
        if '=Nominations=' in line:
            break
    for i in range(len(aprPageLines)):
        end.append(line)
        if '==Special occasion holding area==' in aprPageLines[-i]:
            break
    end.reverse()
    head = '\n'.join(header)
    tail = '\n'.join(end)

    new_apr_page_list = [head,str(aprNoms),tail]
    new_apr_page = '\n'.join(new_apr_page_list)

    page_checks = [nomPageText,approvedPageText]
    msgs = {
        'a': a_msg,
        't': t_msg,
        'c': c_msg,
        'v': v_msg
    }
    success, time = writePages(read,write,new_nom_page,new_apr_page,checks,msgs)

    write_time = time[2] - time[0]
    read_time = time[1] - time[0]
    lag_time = time[2] - time[1]
    times = [read_time,write_time,lag_time]
    times = [str(x) for x in times]

    with open('TimingData.csv','a') as f:
        f.write(','.join(times)+'\n')

    return(success)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        e_name = type(e).__name__
        e_msg = e.message
        fm = "an error in the {{mono|main}} function."
        cm = "been caused by a "+e_name+". See the logs for more info."
        write_error(fm,cm)
        exit()
