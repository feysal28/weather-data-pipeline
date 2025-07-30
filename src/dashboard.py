from data_collection import weather 
import csv
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

#configuration page
st.set_page_config(page_title= "weather in the differents contry", layout = "wide")
st.title("weather contries")

csv_filename = weather()
df = pd.read_csv(csv_filename)

df['update_date'] = pd.to_datetime(df['update_date'], format='%d/%m/%Y, %H:%M:%S')
#selected_town = st.selectbox("Select a town", df['town'].unique())

tab1, tab2, tab3 = st.tabs(["map", "data of contries", "analysis"])

with tab1:
    st.subheader("world map")
    fig = px.scatter_map(
        df,
        lat= "latitude",
        lon="longitude",
        hover_name= "town",
        size= "Temperature",
        color= "Temperature",
        color_continuous_scale=px.colors.sequential.Viridis,
        zoom=3,
        height=600,
        hover_data=["Description", "Humidity (%)"]



    )

    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)


with tab2:
    st.subheader("weather differents contry")
    st.dataframe(df , hide_index=True)

with tab3 :
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 5 - Températures")
        fig_temp = px.bar(
            df.nlargest(5, 'Temperature'),
            x='town',
            y='Temperature',
            color='Temperature',
            text='Temperature',
            labels={'Temperature': '°C'}
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    with col2:
        st.subheader("Humidité par Ville")
        fig_hum = px.bar(
            df,
            x='town',
            y='Humidity (%)',
            #color=0.3,
            color="town"
        )
        st.plotly_chart(fig_hum, use_container_width=True)
    
    st.subheader("Relation Température/Pression")
    fig_scatter = px.scatter(
        df,
        x='Temperature',
        y='Pressure (hPa)',
        color='town',
        size='Humidity (%)',
        hover_name='town'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with st.sidebar:
    st.header("last update")
    latest_update = df['update_date'].max()
    st.write(f"📅 {latest_update.strftime('%d/%m/%Y %H:%M')}")

