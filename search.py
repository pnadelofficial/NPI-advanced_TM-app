import streamlit as st
import pandas as pd
import re

st.title('NPI Data Simple Search')

if 'page_count' not in st.session_state:
    st.session_state['page_count'] = 1

if 'to_see' not in st.session_state:
    st.session_state['to_see'] = 10

if 'start' not in st.session_state:
    st.session_state['start'] = 0

@st.cache
def get_data():
    ref = pd.read_csv('reference.csv')
    ws_ref = pd.read_csv('ws_reference.csv')
    at = pd.read_csv('all_transcripts.csv').rename(columns={'index':'org_index'}).dropna()
    a_s = pd.read_csv('all_written_statements.csv').rename(columns={'index':'org_index', 'answers':'text_clean'}).dropna()
    return at, ref, a_s, ws_ref
all_transcripts, reference, all_statements, ws_reference = get_data()

def escape_markdown(text):
    MD_SPECIAL_CHARS = "\`*_{}[]()#+-!"
    for char in MD_SPECIAL_CHARS:
        text = text.replace(char, '').replace('\t', '').replace('\n', '')
    return text

def display_text(org_index, text):
    text = escape_markdown(text)
    if option == 'Transcripts':
        org_fname = reference.iloc[org_index].filename
    else:
        org_fname = ws_reference.iloc[org_index].filename
    st.write(f'**{org_fname}**')
    st.markdown(f'<p>{text}</p>',unsafe_allow_html=True)
    st.markdown("<hr style='width: 75%;margin: auto;'>",unsafe_allow_html=True)
    return org_fname

search = st.text_input('Search for a word or phrase')

option = st.selectbox(
    'What documents would you like to search in?',
    ('Transcripts', 'Written Statements')
)

if option == 'Transcripts':
    df = all_transcripts
else:
    df = all_statements

if search != '':

    if 'AND' in search:
        s_list = search.split('AND')
        s_list = [f'{s}|{s.lower()}' if s.istitle() else f'{s.title()}|{s}' for s in s_list]
        loc_input = (df.text_clean.str.contains(s_list[0])) & (df.text_clean.str.contains(s_list[1]))
    elif 'OR' in search:
        s_list = search.split('OR')
        s_list = [f'{s}|{s.lower()}' if s.istitle() else f'{s.title()}|{s}' for s in s_list]
        loc_input = (df.text_clean.str.contains(s_list[0])) | (df.text_clean.str.contains(s_list[1]))
    elif 'NOT' in search:
        s_list = search.split('NOT')
        s_list = [f'{s}|{s.lower()}' if s.istitle() else f'{s.title()}|{s}' for s in s_list]
        loc_input = (df.text_clean.str.contains(s_list[0])) & (~df.text_clean.str.contains(s_list[1]))
    else:
        loc_input = df.text_clean.str.contains(search)

    search_trans = df.loc[loc_input]
    st.write(f'There are {len(search_trans)} results for {search}.')
    st.markdown("<hr style='width: 75%;margin: auto;'>",unsafe_allow_html=True)
    search_trans['org_fname'] = search_trans[st.session_state.start:st.session_state.to_see].apply(lambda x: display_text(x['org_index'], x['text_clean']),axis=1)
    
    st.write(f'Page: {st.session_state.page_count} of {len(search_trans)//10}')

    if st.button('See next ten'):
        print('next')
        st.session_state.start = st.session_state.start + 10
        st.session_state.to_see = st.session_state.to_see + 10
        st.session_state.page_count += 1
        print(st.session_state.start, st.session_state.to_see)

    if st.button('See previous ten'):
        print('prev')
        st.session_state.to_see = st.session_state.to_see - 10
        st.session_state.start = st.session_state.start - 10
        st.session_state.page_count -= 1
        print(st.session_state.start, st.session_state.to_see)

    st.download_button(
        label = 'Download data as CSV',
        data = search_trans.to_csv().encode('utf-8'),
        file_name = 'npi_data_excerpt.csv',
        mime = 'text/csv'
    )
