#!/usr/bin/python
# -*- coding: UTF-8 -*-

__version__ = '0.1.0-dev'

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
"""
live = -1

site = pywikibot.Site('en', 'wikipedia')
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

n_text = nomPage.text
a_text = approvedPage.text
all_text = n_text+"\n"+a_text
all_lines = all_text.split("\n")
noms = []
for line in all_lines:
    if "==" in line:
        continue
    elif "<!--" in line:
        continue
    elif "{{" in line:
        noms.append(line)
        
for nom in noms:
    pageTitle = re.search(r"{{.*?nominations\/(.*?)}}",nom).group(1)
    article = pywikibot.Page(pageTitle)
    if article.pageid == 0:
        print("Article does not exist")
        continue
    elif article.isRedirect():
        redirect = article.getRedirectTarget()
        article = pywikibot.Page(redirect)
    talk = article.toggleTalkPage()
    talk_text = talk.text
    if nom in talk_text:
        print("Already notified")
    else:
        if "{{nobots}}" in talk_text:
            continue
        elif "{{bots" in talk_text:
            m = re.search(r"{{bots\|.*?deny=.*?(WugBot).*?(?:\|allow|}})",talk_text)
            try:
                if m.group(1) == "WugBot":
                    continue
            except:
                pass
        talk_text = talk_text + "\n" + nom
    talk.text = talk_text
    talk.save("This article has been nominated at [[WP:DYKN]] to be featured on the main page. WugBot v0.1.0-dev")
        
