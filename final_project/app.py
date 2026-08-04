import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Config
st.set_page_config(page_title="Video Game Industry Trends", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data/Video_Games_Sales_as_at_22_Dec_2016.csv')
    df['Year_of_Release'] = pd.to_numeric(df['Year_of_Release'], errors='coerce')
    df['User_Score'] = pd.to_numeric(df['User_Score'], errors='coerce')
    df = df.dropna(subset=['Year_of_Release', 'Genre', 'Publisher', 'Global_Sales'])
    df['Year_of_Release'] = df['Year_of_Release'].astype(int)
    return df

df = load_data()

st.title("🎮 Video Game Market Evolution & Intelligence")
st.markdown("An interactive analysis of global video game sales, platforms, and critical reception (1980–2016).")

# Sidebar Filters
st.sidebar.header("Filter Visuals")
year_range = st.sidebar.slider("Select Year Range", int(df['Year_of_Release'].min()), int(df['Year_of_Release'].max()), (1995, 2016))
selected_genres = st.sidebar.multiselect("Select Genres", options=df['Genre'].unique(), default=df['Genre'].unique()[:5])

# Filtered Data
filtered_df = df[(df['Year_of_Release'] >= year_range[0]) & 
                 (df['Year_of_Release'] <= year_range[1]) & 
                 (df['Genre'].isin(selected_genres))]

# Key Metrics Highlight Header
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Sales", f"${filtered_df['Global_Sales'].sum():,.2f}M")
m2.metric("Total Games", f"{len(filtered_df):,}")
m3.metric("Top Region", "North America" if filtered_df['NA_Sales'].sum() > filtered_df['EU_Sales'].sum() else "Europe")
m4.metric("Avg Critic Score", f"{filtered_df['Critic_Score'].mean():.1f} / 100" if not filtered_df['Critic_Score'].isna().all() else "N/A")

st.divider()

# Interactive Tabs
tab1, tab2, tab3 = st.tabs(["Regional Trends", "Critic & Score Impact", "Platform Competition"])

with tab1:
    st.subheader("Regional Revenue Shift Over Time")
    reg_trend = filtered_df.groupby('Year_of_Release')[['NA_Sales', 'EU_Sales', 'JP_Sales']].sum().reset_index()
    
    fig_reg = go.Figure()
    fig_reg.add_trace(go.Scatter(x=reg_trend['Year_of_Release'], y=reg_trend['NA_Sales'], name='North America', line=dict(color='#2b5c8f', width=3)))
    fig_reg.add_trace(go.Scatter(x=reg_trend['Year_of_Release'], y=reg_trend['EU_Sales'], name='Europe', line=dict(color='#d95f02', width=3)))
    fig_reg.add_trace(go.Scatter(x=reg_trend['Year_of_Release'], y=reg_trend['JP_Sales'], name='Japan', line=dict(color='#7570b3', width=2)))
    fig_reg.update_layout(template='plotly_white', xaxis_title="Year", yaxis_title="Sales (Millions)")
    st.plotly_chart(fig_reg, use_container_width=True)

with tab2:
    st.subheader("Critic Ratings vs. Market Performance")
    scored = filtered_df.dropna(subset=['Critic_Score'])
    fig_scat = px.scatter(
        scored, x='Critic_Score', y='Global_Sales', color='Genre',
        hover_data=['Name', 'Platform'],
        labels={'Critic_Score': 'Critic Score', 'Global_Sales': 'Global Sales (Millions)'}
    )
    fig_scat.update_layout(template='plotly_white')
    st.plotly_chart(fig_scat, use_container_width=True)

with tab3:
    st.subheader("Top Platforms by Global Sales")
    plat_sales = filtered_df.groupby('Platform')['Global_Sales'].sum().nlargest(10).reset_index()
    fig_plat = px.bar(plat_sales, x='Platform', y='Global_Sales', color_discrete_sequence=['#2b5c8f'])
    fig_plat.update_layout(template='plotly_white', yaxis_title="Global Sales (Millions)")
    st.plotly_chart(fig_plat, use_container_width=True)