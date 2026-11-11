import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv ("Unicorn_Companies.csv")
    # data cleaning
    # replace NaN in City & Select Investors Columns
    capitals = {"Bahamas":"Nassau","Singapore":"Singapore City","Hong Kong":"Hong Kong City"}
    df.loc[:,"City"] = df['City'].fillna(df['Country/Region'].map(capitals))
    df.fillna({"Select Investors":"None","City":"N/A"}, inplace=True)

    # Cleaning the Valuation & Funding columns
    df["Valuation"] = df["Valuation"].str.replace('$',"").str.replace("B","000000000")
    # Convert the data type
    df["Valuation"] = df["Valuation"].astype("float64")
    # Funding
    df["Funding"] = df["Funding"].str.replace('$',"")\
    .str.replace("B","000000000")\
    .str.replace("M","000000").str.replace('Unknown',"-1").astype("float64")
    # Date joined - conversion
    df["Date Joined"] = pd.to_datetime(df["Date Joined"])
    df['Year Joined'] = df['Date Joined'].dt.year
    return df

try:
    df = load_data()
    # App title
    st.title("Unicorn Companies Analysis App")
    # st.dataframe(df.head(10))

    # Sidebar
    st.sidebar.title("Dashboard Filter")
    # Filters for country, industry etc
    countries = df["Country/Region"].unique()
    industries = df["Industry"].unique()
    continent = df["Continent"].unique()
    # Date filter in slider form
    year_min = int(df["Year Joined"].min())
    year_max = int(df["Year Joined"].max())

    if year_min < year_max:
        year_range = st.sidebar.slider(
        "Year Joined", min_value=year_min, max_value=year_max,
        value=(year_min, year_max))
    else:    
        year_range = (year_min, year_max)
    # Create the multi-select box in the app sidebar
    selected_industries = st.sidebar.multiselect(
    "Select Industry", industries, default=industries)

    Selected_countries = st.sidebar.multiselect(
    "Select Country", countries, default=countries)

    Selected_continent = st.sidebar.multiselect(
    "Select Continent", continent, default=continent)

    # Apply the filters selected
    filtered_df = df[(df["Industry"].isin(selected_industries)) &
                     (df["Continent"].isin(Selected_continent)) &
                     (df["Country/Region"].isin(Selected_countries)) 
                    ].copy()

    # Display the filtered data
    st.dataframe(filtered_df)

    # Format long numbers 
    def billions_format(value):
        return f"${value / 1_000_000_000:,.2f}B"

    def trillions_format(value):
        return f"${value / 1_000_000_000_000:,.2f}T"

    # Global Overview
    st.header("1. Global Overview")
    if not filtered_df.empty:
        total_companies = filtered_df["Company"].nunique()
        total_valuation = filtered_df["Valuation"].sum()
        total_funding = filtered_df["Funding"].sum()
        avg_valuation = filtered_df["Valuation"].mean()

        col1,col2,col3,col4 = st.columns(4)
        col4, col5 = st.columns(2)
  
        col1.metric("Total Unicorns",f"{total_companies:,}")
        col2.metric("Combined Valuation",trillions_format(total_valuation))
        col3.metric("Average Valuation",billions_format(avg_valuation))
        col4.metric("Total Funding",billions_format(total_funding))

        # Simple charts
        col6, col7 = st.columns(2)
        with col6:
            industry_counts = (
                filtered_df['Industry'].value_counts().reset_index()
            )
        industry_counts.columns = ["Industry", "Companies"]

        fig = px.pie(
        industry_counts,
        names="Industry",
        values="Companies",
        hole=0.45,
        title="Unicorns by Industry"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col7:
        industry_counts = (
                filtered_df["Continent"].value_counts().reset_index()
            )
        industry_counts.columns = ["Continent", "Companies"]

        fig = px.bar(
        industry_counts,
        x="Continent",
        y="Companies",
        color="Continent",
        title="Unicorns by Continent"
        )
        st.plotly_chart(fig, use_container_width=True)
        
except URLError as e:
    st.error(
        """
        **File Not Found.**
        Connection error: %s
    """
        %e.reason 
)