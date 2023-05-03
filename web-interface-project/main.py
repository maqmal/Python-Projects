import pandas as pd
import numpy as np
import streamlit as st
from utils import *
import plotly.express as px


def data_exploration_page(df):
    st.markdown("# Data Exploration and Cleansing")
    df_option = df.copy()
    options = st.selectbox('View Data Option:',('Raw Data', 'Bots with No Features', 'Same Bots Name'))
    if options=='Raw Data':
        st.write(df_option)
    if options=='Bots with No Features':
        st.write(df_option[(~df_option.select_dtypes(bool)).all(axis=1)])
    if options=='Same Bots Name':
        st.write(df_option[df_option.duplicated(['Chatbot name'])])

    st.markdown("### Handling NaN Value.")
    st.markdown("Terlihat ada nilai `NaN` pada data.")
    df_nan = pd.DataFrame(df.isna().sum()).rename(columns={0:'Jumlah nilai NaN'})
    st.write(df_nan)
    
    df.replace(np.NaN, 'Undefined', inplace=True)

    st.markdown('''Kolom `Industry` dan `AM Name` memiliki nilai `NaN`. 
    Data yang memiliki nilai `NaN` akan diganti dengan `Undefined` untuk mempermudah memahami data.''')
    if st.button("Show Result"):
        if st.button("Hide Result"):
            st.write()
        st.write(df)

    st.markdown("### Inactive Chatbots.")
    st.write(df[(~df.select_dtypes(bool)).all(axis=1)].drop(columns=['Industry','AM Name']))
    st.markdown("Terdapat 8 chatbots yang memiliki nilai `False` pada semua fiturnya, maka dari itu chatbots tersebut akan dihapus.")
    df = df.drop(index=df[(~df.select_dtypes(bool)).all(axis=1)].index)

    st.markdown("### Duplicate Chatbots Name.")
    duplicate_row = df[df.duplicated(['Chatbot name'])]
    st.write(duplicate_row['Chatbot name'])
    st.markdown('''Terdapat nama chatbot yang sama sehingga perlu diolah agar dapat dihitung tingkat similarity nya. 
    Nama bots yang sama akan ditambahkan nama industri nya pada bagian belakang namanya.''')
    df['Chatbot name'] = df['Chatbot name'].where(~df['Chatbot name'].duplicated(), df['Chatbot name'] +'_'+df['Industry'])
    if st.button("Show Duplicate"):
        if st.button("Hide Duplicate"):
            st.write()
        st.write(df[df['Chatbot name'].str.contains("_")]['Chatbot name'])

    st.write("# Data Ready to Use")
    df = df.drop(columns=['Industry','AM Name'])
    df = df.set_index('Chatbot name')
    st.write(df)
    

def similarity_page(data):
    st.markdown('''
    # Similarity Distance Matrix

    Mencari Chatbots yang mirip dengan bots lainnya.

    Perhitungan similarity antar chatbot menggunakan fungsi `Jaccard Distance`. 
    ''')
    df = clean_data(data)
    df = df.drop(columns=['Industry','AM Name'])
    df = df.set_index('Chatbot name')
    num_bot = st.sidebar.number_input('Choose The Top Similar Bots', 1, 30)
    similar = similarity(df, num_bot)
    st.write(similar)
    st.markdown('Perhitungan similarity berdasarkan Jaccard Distance terendah.')
    options = st.selectbox('Pilih bots untuk melihat nilai distance nya:',(similar.index))
    for i in range(len(similar.index)):
        if options==similar.index[i]:
            single,tes = single_sim(df, similar.index[i],num_bot)
            st.write(tes)

            viz = visualize_data(all_sim(df,similar.index[i]), similar.index[i])
            st.write(viz)

def clustering_page(data):
    st.markdown("# Chatbots Clustering")
    st.markdown('Mengelompokkan chatbots berdasarkan jumlah cluster tertentu.' )
    st.markdown('Algoritma Clustering yang digunakan adalah `K-modes`. Algoritma ini cocok digunakan untuk data categorial.')
    num_cluster = st.sidebar.number_input('Choose The Number of Cluster', 2, 10)
    
    cluster = k_modes(data, num_cluster)
    keys = sorted(list(cluster["Cluster"].unique()))
    keys = ['Cluster ' + str(s) for s in keys]
    cluster = st.selectbox("Pilih cluster yang ingin ditampilkan:", keys, index=0)
    cluster_result = cluster.split(' ')[1]
    preview_df = preview_cluster(data, int(cluster_result))
    st.write(preview_df)
    st.write('### Radar Chart')
    st.write(make_radar_chart(data, num_cluster))

def home(df):
    st.sidebar.markdown("# Project Data Chat Bot - Berfaedah")
    page = st.sidebar.radio('Choose what to see:',('Data Exploration','Chatbots Similarity','Chatbots Clustering'))
    if page=='Data Exploration':
        data_exploration_page(df)
    if page=='Chatbots Similarity':
        similarity_page(df)
    elif page=='Chatbots Clustering':
        clustering_page(clean_data(df))
 

if __name__ == '__main__':
    home(pd.read_csv('interntask.csv'))
