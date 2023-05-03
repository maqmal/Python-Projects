import pandas as pd
import numpy as np
import scipy.spatial
import streamlit as st
from kmodes.kmodes import KModes
import plotly.graph_objects as go
from math import pi
from matplotlib import cm
import altair as alt

def preview_cluster(df, cluster):
    df = df[df['Cluster'] == cluster]
    return df

def clean_data(data):
    data.replace(np.NaN, 'Undefined', inplace=True)
    data = data.drop(index=data[(~data.select_dtypes(bool)).all(axis=1)].index)
    data['Chatbot name'] = data['Chatbot name'].where(~data['Chatbot name'].duplicated(), data['Chatbot name'] +'_'+data['Industry'])

    return data

def visualize_data(data,user):
    graph = alt.Chart(data).mark_bar().encode(
        x=user,
        y='Value',).interactive()

    return graph

def all_sim(data,user):
    jaccard = scipy.spatial.distance.cdist(data, data,  
                                       metric='jaccard')

    user_distance = pd.DataFrame(jaccard, columns=data.index.values,  
                             index=data.index.values)
    # extract the distances of the column ranked by smallest
    distance = user_distance[user].nsmallest(len(user_distance))
    # for each user, create a key in the dictionary and assign a list that contains a ranking of its most similar users
    simmilar = [i for i in distance.index if i!=user]
    val = [i for i in distance.values if i!=0]
    name_data = {user:simmilar, 'Value':val}
    df = pd.DataFrame(name_data)
    return df

def single_sim(data,user,top_rank):
    jaccard = scipy.spatial.distance.cdist(data, data,  
                                       metric='jaccard')

    user_distance = pd.DataFrame(jaccard, columns=data.index.values,  
                             index=data.index.values)
    # extract the distances of the column ranked by smallest
    distance = user_distance[user].nsmallest(len(user_distance))
    # for each user, create a key in the dictionary and assign a list that contains a ranking of its most similar users
    simmilar = [i for i in distance.index if i!=user]
    val = [i for i in distance.values if i!=0]
    name_data = {user:simmilar[:top_rank], 'Value':val[:top_rank]}
    df = pd.DataFrame(name_data)
    lol = df.set_index(user).T
    return df, lol

def similarity(data, top_rank):
    jaccard = scipy.spatial.distance.cdist(data, data,  
                                       metric='jaccard')

    user_distance = pd.DataFrame(jaccard, columns=data.index.values,  
                             index=data.index.values)

    user_rankings = {}
    for user in user_distance.columns:
        # extract the distances of the column ranked by smallest
        distance = user_distance[user].nsmallest(len(user_distance))
        # for each user, create a key in the dictionary and assign a list that contains a ranking of its most similar users
        simmilar = [i for i in distance.index if i!=user]
        name_data = {user : simmilar[:top_rank]}
        user_rankings.update(name_data)

    data = pd.DataFrame(user_rankings).T
    data_sim = pd.DataFrame(user_rankings)
    for i in range(top_rank):
        data.rename(columns={(i): "Rank {}".format(i+1)}, inplace=True)

    return data

def k_modes(data, n_cluster):
    km = KModes(n_cluster, init='Huang', n_init=5, verbose=1)
    clusters = km.fit_predict(data)

    data['Cluster'] = clusters
    data = data[['Chatbot name','Industry','AM Name','Cluster']].sort_values(by=['Cluster'])

    return data


@st.cache(allow_output_mutation=True)
def make_radar_chart(norm_df, n_clusters):
    fig = go.Figure()
    cmap = cm.get_cmap('tab20b')
    angles = list(norm_df.columns[3:])
    angles.append(angles[0])
    for i in range(n_clusters):
        subset = norm_df[norm_df['Cluster'] == i]
        data = [np.mean(subset[col]) for col in angles[:12]]
        data.append(data[0])
        fig.add_trace(go.Scatterpolar(
            r=data,
            theta=angles,
            # fill='toself',
            # fillcolor = 'rgba' + str(cmap(i/n_clusters)),
            mode='lines',
            line_color='rgba' + str(cmap(i/n_clusters)),
            name="Cluster " + str(i)))
        
    fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1])
                ),
            showlegend=True
    )
    fig.update_traces()
    return fig

