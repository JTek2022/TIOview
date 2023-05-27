# -*- coding: utf-8 -*-
"""
Created on Thu May 25 12:09:56 2023

@author: JtekG
"""

import streamlit as st

from st_aggrid import AgGrid
import pandas as pd
import re

# set the page icon and title
# may not be useful in the iframe
st.set_page_config(page_title='TIO log Viewer Dashboard',  layout='wide', page_icon='https://noctrixhealth.com/wp-content/uploads/2021/05/cropped-SiteIcon-32x32.jpg')


# remove the orange/red line on top
# also hides the hamburger menu
hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
        footer {visibility: hidden;} 
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


def LEDdecoder():

    col1, col2, col3, col4, col5 = st.columns(5)
    led1 = col1.checkbox(label="LED 1")
    led2 = col2.checkbox(label="LED 2")
    led3 = col3.checkbox(label="LED 3")
    led4 = col4.checkbox(label="LED 4")
    led5 = col5.checkbox(label="LED 5")
    
        
    if led1 and not (led2 or led3 or led4):
        st.write("No Therapy sessions recorded")
        
    if (led1 and led2) and not (led3 or led4):
        st.write("1 or two therapy sessions recorded")
        
    if (led1 and led2 and led3) and not (led4):
        st.write("3 or 4 therapy sessions recorded")
    
    if (led1 and led2 and led3 and led4):
        st.write("5+ therapy sessions recorded")
    
    if (led1 and led2 and led5):
        st.write("and >75% of sessions ended at higher than L1")

def tioLogViewer():
    uploaded_files = st.file_uploader("Drag a TIO created log file", accept_multiple_files=True)
    theList = []
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        st.write("filename:", uploaded_file.name)
        theList = (bytes_data.splitlines())

    # timestamp format [00:00:31.667,968]
    lvlRegEx = r"<[a-zA-Z]{3}>"
    tsRegEx = r"\d{2}:\d{2}:\d{2}.\d{3},\d{3}"
    logDF = pd.DataFrame()
    logList = []
    
    for line in theList:
        fullLine = str(line)
        
        timestamp = ""
        lvl = ""
        

        
        thread = fullLine.split('>',maxsplit=1)[-1].split(':',maxsplit=1)[0]
        
        fullLine = fullLine.replace(thread,"")
        
        timestampSearch = re.search(tsRegEx, fullLine)
        if timestampSearch:
            timestamp = timestampSearch.group(0)
            fullLine = fullLine.replace('['+timestamp+']','') # take out timestamp from string
        
        
        lvlSearch = re.search(lvlRegEx, fullLine)
        if lvlSearch:
            lvl = lvlSearch.group(0)
        
        patterns = {r"b'": "", r"\x1b": "", r"1;32muart:~$": "",
                    r"[0m'":"", r"[0m":"", r"[m[8D[J":"",
                    thread:"", lvl:""}

        for pattern, replacement in patterns.items():
            fullLine = fullLine.replace(pattern, replacement)
        
        if fullLine == "":
            fullLine = thread
            thread = ""
            
        outRow = {'Timestamp':timestamp,
                  'Debug':lvl,
                  'thread':thread.strip(),
                  'remain':fullLine,
                  'raw':str(line)}
        
        logList.append(pd.DataFrame(outRow,index=[0]))
        

    if len(logList) > 0:
        logDF = pd.concat(logList, ignore_index=True)
    
        AgGrid(logDF)
        

# page2use = st.sidebar.radio(label="Choose tool", options=["LED Decoder","tio log viewer"])
# if page2use == "LED Decoder":
#     LEDdecoder()
# if page2use == "tio log viewer":
#     tioLogViewer()

tioLogViewer()

        