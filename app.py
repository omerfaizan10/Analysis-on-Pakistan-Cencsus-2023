import streamlit as st
import pandas as pd
import plotly.express as px
# Load your data once
@st.cache_data
def load_data():
    return pd.read_csv('merged.csv')
df = load_data()
# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
# Define navigation logic
def go_to_dashboard():
    st.session_state.page = 'dashboard'
# ========== PAGE: WELCOME ==========
if st.session_state.page == 'welcome':
    st.title("🇵🇰 Pakistan Census 2023")
    st.markdown("""
    Welcome to the **Pakistan Census Dashboard by EngD. Omer Faizan** —  
    Explore insights on population, literacy, gender, and educational institutions across Pakistan’s districts.

    📊 Powered by Streamlit  
    🔍 Based on 1998–2023 datasets
    """)
    if st.button("🚀 Explore the Analysis"):
        go_to_dashboard()
# ========== PAGE: DASHBOARD ==========
elif st.session_state.page == 'dashboard':
    st.title("📊 Pakistan Census - District Level Analysis")

    province = st.selectbox("Select a Province", df['province'].unique())
    df_filtered = df[df['province'] == province].copy()

    df_filtered['population_growth_%'] = (
        (df_filtered['population_2023'] - df_filtered['population 1998']) / df_filtered['population 1998']
    ) * 100

    top_growth = df_filtered.sort_values(by='population_growth_%', ascending=False).head(10)

    fig_growth = px.bar(
        top_growth,
        x='district',
        y='population_growth_%',
        color='district',
        title=f"Top 10 Growing Districts in {province}",
        labels={'population_growth_%': 'Growth %'}
    )
    st.plotly_chart(fig_growth, key="growth")

    st.header("📘 Literacy Rate vs Population (by District)")
    if 'literacy_rate' not in df.columns:
        df['literacy_rate'] = df['total_schools'] / df['population_2023'] * 100

    fig_lit_pop = px.scatter(
        df,
        x='population_2023',
        y='literacy_rate',
        color='province',
        size='total_schools',
        hover_name='district',
        hover_data=['male', 'female', 'total_schools'],
        title="Literacy Rate vs Population (District-wise)",
        labels={
            'population_2023': 'Population (2023)',
            'literacy_rate': 'Estimated Literacy Rate (%)'
        },
        template='plotly_white'
    )
    st.plotly_chart(fig_lit_pop, key="lit_pop")

    st.header("🏫 Districts with Highest People per School")
    df['people_per_school'] = df['population_2023'] / df['total_schools']
    df_school_filtered = df[df['total_schools'] > 0].copy()
    underserved = df_school_filtered.sort_values(by='people_per_school', ascending=False).head(10)

    fig_underserved = px.bar(
        underserved,
        x='district',
        y='people_per_school',
        color='province',
        title='Top 10 Underserved Districts by School Access',
        labels={'people_per_school': 'People per School'},
        hover_data=['population_2023', 'total_schools']
    )
    st.plotly_chart(fig_underserved, key="underserved")

    st.header("👥 Gender Imbalance Across Districts")
    df_gender = df[df['female'] > 0].copy()
    df_gender['male_female_ratio'] = df_gender['male'] / df_gender['female']

    top_male_skewed = df_gender.sort_values(by='male_female_ratio', ascending=False).head(10)
    top_female_skewed = df_gender.sort_values(by='male_female_ratio', ascending=True).head(10)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔵 Male-Dominant Districts")
        fig1 = px.bar(
            top_male_skewed,
            x='district',
            y='male_female_ratio',
            color='province',
            labels={'male_female_ratio': 'Male/Female Ratio'},
            title='Top 10 Male-Skewed Districts'
        )
        st.plotly_chart(fig1, key="male_skewed")

    with col2:
        st.subheader("🔴 Female-Dominant Districts")
        fig2 = px.bar(
            top_female_skewed,
            x='district',
            y='male_female_ratio',
            color='province',
            labels={'male_female_ratio': 'Male/Female Ratio'},
            title='Top 10 Female-Skewed Districts'
        )
        st.plotly_chart(fig2, key="female_skewed")

    st.header("🏙️ Most Densely Populated Districts (Urban Proxies)")
    top_dense = df.sort_values(by='density_2023(people/km²)', ascending=False).head(10)
    fig_dense = px.bar(
        top_dense,
        x='district',
        y='density_2023(people/km²)',
        color='province',
        title="Top 10 Densely Populated Districts",
        labels={'density_2023(people/km²)': 'People per km²'}
    )
    st.plotly_chart(fig_dense, key="density")

    # Literacy vs Total Schools
    st.header("📈 Literacy Rate vs Total Number of Schools")
    if 'literacy_rate' not in df.columns:
        df['literacy_rate'] = (df['total_schools'] / df['population_2023']) * 100
    df_corr = df[(df['literacy_rate'] > 0) & (df['total_schools'] > 0)].copy()

    fig_corr = px.scatter(
        df_corr,
        x='total_schools',
        y='literacy_rate',
        size='population_2023',
        color='province',
        hover_name='district',
        title='Correlation Between Total Schools and Literacy Rate',
        labels={
            'total_schools': 'Total Schools',
            'literacy_rate': 'Literacy Rate (%)'
        }
    )
    st.plotly_chart(fig_corr, key="school_lit_corr")
    st.info("""
📌 **What This Shows**:
- Districts with more schools **tend to have higher literacy**, but it’s not always linear.
- Some districts with many schools still struggle with literacy — likely due to **quality**, **access**, or **gender imbalance**.
- **Punjab** and **Sindh** show better clustering toward higher literacy.

This insight can be used to identify districts where investment in **teacher training**, **school quality**, or **female access** may be more effective than just building more schools.
""")

    st.header("📈 Population vs Total Schools")
    df_clean = df[(df['population_2023'] > 0) & (df['total_schools'] > 0)]
    fig_pop_school = px.scatter(
        df_clean,
        x='population_2023',
        y='total_schools',
        color='province',
        hover_name='district',
        title='Total Schools vs Population (by District)',
        labels={
            'population_2023': 'Population (2023)',
            'total_schools': 'Total Schools'
        },
        template='plotly_white'
    )
    st.plotly_chart(fig_pop_school, key='pop_school_scatter')
