# -*- coding: utf-8 -*-
"""
Created on Thu May 25 12:09:56 2023

@author: JtekG
"""

import streamlit as st

from st_aggrid import AgGrid, GridOptionsBuilder

import pandas as pd
import re
import openpyxl

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
    with st.spinner('Parsing text...'):
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
                        r"[0m'":"", r"[0m":"", r"[m[8D[J":"","[1;33m":"",":":"","[":"",
                        thread:"", lvl:""}
    
            for pattern, replacement in patterns.items():
                fullLine = fullLine.replace(pattern, replacement)
            
            if fullLine == "":
                fullLine = thread
                thread = ""
                
            outRow = {'Timestamp':timestamp,
                      'Debug':lvl,
                      'thread':thread.strip(),
                      'log':fullLine,
                      'raw':str(line)}
            
            logList.append(pd.DataFrame(outRow,index=[0]))
        

    if len(logList) > 0:
        logDF = pd.concat(logList, ignore_index=True)
        #logDF
        #AgGrid(logDF)

        logDF.to_excel("my_file.xlsx")
        # Load the Excel file
        workbook = openpyxl.load_workbook('my_file.xlsx')
        worksheet = workbook['Sheet1']
        
        # Add filters to the worksheet
        worksheet.auto_filter.ref = worksheet.dimensions
        for col in worksheet.iter_cols():
            worksheet.auto_filter.add_filter_column(col[0].col_idx - 1, [])

        # Save the filtered Excel file
        newFileName = str(uploaded_file.name).replace(".txt","xlsx")
        workbook.save(newFileName)
        
        
        # add a download button for the file
        with open(newFileName, 'rb') as f:
            data = f.read()
        st.download_button(
            label='Download Tio Excel file',
            data=data,
            file_name=newFileName,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        with st.expander("See spreadsheet here 100 row per page"):
            # configure grid options
            gob = GridOptionsBuilder.from_dataframe(logDF)
            gob.configure_pagination(paginationPageSize=100)  # set page size to 2 rows
            grid_options = gob.build()
            AgGrid(logDF, gridOptions=grid_options)
        

# page2use = st.sidebar.radio(label="Choose tool", options=["LED Decoder","tio log viewer"])
# if page2use == "LED Decoder":
#     LEDdecoder()
# if page2use == "tio log viewer":
#     tioLogViewer()

tioLogViewer()

        