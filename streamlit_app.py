import altair as alt
import pandas as pd
import streamlit as st

### P1.2 ###


@st.cache_data
def load_data():
    
    cancer_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/cancer_ICD10.csv").melt(  # type: ignore
    id_vars=["Country", "Year", "Cancer", "Sex"],
    var_name="Age",
    value_name="Deaths",)
    
    pop_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/population.csv").melt(  # type: ignore
    id_vars=["Country", "Year", "Sex"],
    var_name="Age",
    value_name="Pop",)

    df = pd.merge(left=cancer_df, right=pop_df, how="left")
    df["Pop"] = df.groupby(["Country", "Sex", "Age"])["Pop"].fillna(method="bfill")
    df.dropna(inplace=True)

    df = df.groupby(["Country", "Year", "Cancer", "Age", "Sex"]).sum().reset_index()
    df["Rate"] = df["Deaths"] / df["Pop"] * 100_000
    return df

df = load_data()

### P1.2 ###

st.write("## Age-specific cancer mortality rates")

### P2.1 ###
# replace with st.slider
year = st.slider(label='Year', 
          min_value=1994, max_value=2020, 
          value=None, step=None, format=None, key=None, help=None, on_change=None, args=None, kwargs=None, 
          disabled=False, label_visibility="visible")
### P2.1 ###


### P2.2 ###
# replace with st.radio
sex_options = ('M', 'F')
def sex_internal_function(sex):
    return 'F' if sex == 'F' else 'M'

sex = st.radio(label='Sex', options = sex_options, index=0, 
         format_func=sex_internal_function, 
         label_visibility="visible")
### P2.2 ###


### P2.3 ###
# replace with st.multiselect
# (hint: can use current hard-coded values below as as `default` for selector)
countries_list = df['Country'].unique().tolist()
countries_sub = ["Austria", "Germany","Iceland","Spain","Sweden","Thailand"]

def country_internal_function(country):
    return country

countries = st.multiselect(label = 'Countries', options= countries_list, default=countries_sub, 
               format_func=country_internal_function, placeholder="Choose an option", disabled=False, label_visibility="visible")
### P2.3 ###


### P2.4 ###
# replace with st.selectbox
cancer_list = df['Cancer'].unique().tolist()
def cancer_internal_function(cancer):
    return cancer

cancer = st.selectbox(label='Cancer', options=cancer_list, index=0, 
             format_func=cancer_internal_function, placeholder="Choose an option", disabled=False, label_visibility="visible")
### P2.4 ###

# Filter based on user selections
subset = df[(df['Sex'] == sex) & (df['Country'].isin(countries)) & (df['Cancer'] == cancer)]

### P2.5 ###
ages = [
    "Age <5",
    "Age 5-14",
    "Age 15-24",
    "Age 25-34",
    "Age 35-44",
    "Age 45-54",
    "Age 55-64",
    "Age >64",
]

# Configure common options. 
def log_transform(rate):
    return 0.01 if rate == 0 else rate

subset['log_rate'] = subset['Rate'].apply(log_transform)

base = alt.Chart(subset).encode(
    x=alt.X("Age", sort=ages),
    y=alt.Y('Country:N', title='Country'),
)

# Configure heatmap
heatmap = base.mark_rect().encode(
    alt.Color('log_rate:Q')
        .scale(type='log', domain=[0.01, 100], scheme='blues')
        .title("Mortality rate per 100k"), 
        tooltip=[alt.Tooltip('Rate:Q', title='Rate: ')]
).properties(title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",)

st.altair_chart(heatmap, use_container_width=True)

population_data = subset.groupby('Country')['Pop'].sum().reset_index()

chart = alt.Chart(population_data).mark_bar().encode(
    x=alt.X('Population:Q', title='Total Population'),
    y=alt.Y('Country:N', title='Country', sort='-x'),
    tooltip=[
        alt.Tooltip('Population:Q', title='Sum of Population: '),
        alt.Tooltip('Country:N', title='Country: ')])

st.altair_chart(chart, use_container_width=True)

### P2.5 ###

st.altair_chart(chart, use_container_width=True)

countries_in_subset = subset["Country"].unique()
if len(countries_in_subset) != len(countries):
    if len(countries_in_subset) == 0:
        st.write("No data avaiable for given subset.")
    else:
        missing = set(countries) - set(countries_in_subset)
        st.write("No data available for " + ", ".join(missing) + ".")
