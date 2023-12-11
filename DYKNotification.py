#!/usr/bin/python
# -*- coding: UTF-8 -*-

__version__ = '0.4.0-dev'

import re
import os
import codecs
import timeit
from copy import copy
from random import shuffle

import logging
import pywikibot
import datetime

"""
CONFIGURATION VARIABLES

The following variables toggle the way the bot interacts with pages and their
    setting should reflect consensus.
ATTRIBUTE   VALUES  DESCRIPTION
live         0      Testing mode. Reads from the live DYKN pages. Writes to
                      test pages only.
             1      Live mode. The bot is live and edits outside Userspace.
                      This mode should not be used without approval from the
                      Bot Approval Group on the English Wikipedia.
"""
live = 1
_debug_n = 0
_n=0

def editLink(nom):
    pref = "https://en.wikipedia.org/w/index.php?title="
    if "Template:" not in nom:
        pref = pref+"Template:"
    title = nom.lstrip("{").rstrip("}").strip().replace(" ","_")
    action = "&action=edit"
    url = pref + title + action
    return(url)
    
def already_notified(text):
    dyk_regex = r'\{\{.*?Did(?: |_)you(?: |_)know(?: |_)nominations\/.*?\}\}'
    matches = re.search(dyk_regex,text)
    if matches:
        return(True)
    else:
        return(False)

def is_nom(line):
    status = already_notified(line)
    return(status)
        
def excluded(text):
    if "{{nobots}}" in text:
        return(True)
    elif "{{bots" in text:
        m = re.search(r"{{bots\|.*?deny=.*?(WugBot).*?(?:\|allow|}})",text)
        if m:
            return(True)
        else:
            return(False)
    else:
        return(False)
        
def pages(live,test_page='User:WugBot/DYKNoteTest'):
    if live == 1:
        read  = 'Template talk:Did you know'
        write = None
    else:
        read = test_page
        write = 'User:Wugapodes/DYKTest'
    io = (read,write)
    return(io)
    
def main():
    global live
    global _n
    global _debug_n
    site = pywikibot.Site('en', 'wikipedia')
    read,write = pages(live)
    nomPage = pywikibot.Page(site,read)
    approvedPage = pywikibot.Page(site,read+'/Approved')
    
    n_text = nomPage.text
    a_text = approvedPage.text
    all_text = n_text+"\n"+a_text
    all_lines = all_text.split("\n")
    noms = []
    for line in all_lines:
        if is_nom(line):
            noms.append(line)
            
    # For Testing Purposes
    if live != 1:
        shuffle(noms)
            
    for nom in noms:
        if _n == _debug_n and _debug_n > 0:
            break
        try:
            pageTitle = re.search(r"{{.*?nominations\/(.*?)}}",nom).group(1)
        except:
            print(nom)
            continue
        article = pywikibot.Page(site,pageTitle)
        if article.pageid == 0:
            print("Article %s does not exist" % pageTitle)
            continue
        elif article.isRedirectPage():
            redirect = article.getRedirectTarget().title()
            try:
                article = pywikibot.Page(site,redirect)
            except:
                print("Could not retrieve redirect target "+redirect)
                continue
        talk = article.toggleTalkPage()
        talk_text = talk.text
        if already_notified(talk_text):
            print("Already notified")
            continue
        if excluded(talk_text):
            continue
        talk_text = talk_text + "\n\n==Did you know nomination==\n" + nom
        if live != 1:
            talk = pywikibot.Page(site,write)
        talk.text = talk_text
        talk.save("This article has been nominated at [[WP:DYKN]] " \
                    + "to be featured on the main page. WugBot v"+__version__)
        _n += 1
        
if __name__ == "__main__":
    main()
