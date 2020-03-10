import streamlit as st
import numpy as np 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import censusdata


st.image(image='censusimg.jpg',caption='https://pixabay.com/illustrations/magnifying-glass-human-head-faces-1607208/')

st.title('Census Data Exploration')
st.header('Explore socially important metrics')
st.write('This exploration uses data from American Community Survey 5-year data released in 2017.')
st.write('More information about the ACS 5-year survey: https://www.census.gov/data/developers/data-sets/acs-5year.html')
st.write("The data was collected using Julien Leider's CensusData pip package, which can be found at https://pypi.org/project/CensusData/ or installed with")
st.code('pip install CensusData')

st.header('County Level Summaries')
st.write('This analysis will use data aggregated on the county level for the variables: Gini Index (income inequality index), Vacant Housing, Percent Unemployed and Median Family Income.')


### SECTION 1: Querying and Cleaning Data ###

# Query the CensusData API
def ApiQuery():

    try: 
        # Query the data and save to a dataframe
        df = censusdata.download('acs5', 2018,
                                censusdata.censusgeo([('state', '*'),('county', '*')]),var=
                                ['B19083_001E','B19113_001E','B23025_003E','B23025_005E','B01001_001E','B25004_001E'])
    except: 
        print('Could not query data.')

    df = df.reset_index()
    df.columns = ['Location','gini_index','median_family_income','employed','unemployed','population',
                'vacant_housing']

    return df


# Parse the "Location" column for County and State FIPS Ids.
def FindFipsId(df):

    # Set the Location variable as type string
    df.Location = df.Location.astype(str)

    # Drop Puerto Rico (Sorry!!!)
    df = df[df['Location'].str.contains("Puerto Rico:")==False]

    # Define a lambda expression to extract the state fips ID, and apply to the dataframe.
    state_fips = lambda a: a[a.find('state:')+6:a.find('state:')+8]
    df['state_fips'] = df['Location'].apply(state_fips)

    # Define a lambda expression to extract the county fips, and apply to the dataframe.
    county_fips = lambda a: a[a.find('county:')+7:a.find('county:')+11]
    df['county_fips'] = df['Location'].apply(county_fips)

    # Combine the two strings for the state and county fips to a single fips identifier. 
    df['fips'] = df.state_fips+df.county_fips
    df.fips = df.fips.astype('int32')

    # Define a lambda expression to extract the county name, and apply to the dataframe
    county_name = lambda a: a[:a.find('County,')+6]
    df['county_name'] = df['Location'].apply(county_name)

    # Convert state fips and county fips to numeric values
    df['state_fips'] = pd.to_numeric(df.state_fips)
    df['county_fips'] = pd.to_numeric(df.county_fips)


    # Drop Location as it is has been parsed into multiple variables.
    # It is a long string, and unnecessary.
    df = df.drop('Location',axis=1)    

    return df


# Calculate a percent_unemployed column
def PctUnemployed(df):

    df['percent_unemployed'] = df.unemployed / df.employed * 100

    return df


def OnlyColumns(df):

    # Return only the necessary columns for analysis
    df = df[['gini_index','vacant_housing','percent_unemployed', 'median_family_income']]
    # Rename the columns
    df.columns = ['Gini Index', 'Vacant Housing', 'Percent Unemployed', 'Median Family Income']

    return df


# Execute the ApiQuery function to retrieve the data.
df = ApiQuery()

# Find the FIPS Id by parsing the location string column.
df = FindFipsId(df)

# Calculate percent unemployed.
df = PctUnemployed(df)

# Select only the necessary columns.
df = OnlyColumns(df)


### SECTION 2: Display the data.


# Dataframe for median family income Statistics
st.subheader('Descriptive Statistics for Median Family Income')
st.write(df['Median Family Income'].describe().round())

# Histogram for median family income
st.subheader('Seaborn distplot of Median Family Income')
plt.figure()
plt.title('County Level Income Distribution')
sns.set_style('darkgrid')
sns.distplot(df['Median Family Income'])
st.pyplot()

# Create a new column based on median family income called 'Income Quartile'.
df['Income Quartile'] = pd.qcut(df['Median Family Income'],q=4,labels=False,precision=0,duplicates='raise')
# Zero-based, raise by 1
df['Income Quartile'] = df['Income Quartile'] + 1

# Scatterplot for median family income by quartile
st.subheader('Seaborn scatterplot of Median Family Income by Percent Unemployed')
plt.figure()
sns.set_style('darkgrid')
plt.title('Median Family Income versus Unemployment')
sns.scatterplot(x='Median Family Income',y='Percent Unemployed',data=df,hue='Income Quartile',palette="Dark2")
st.pyplot()

# Checkbox for lmplot analysis
st.subheader('Please select an X and Y value for analysis' )
x_axis = st.selectbox(
    'Pick an X-axis value:',
     ['Gini Index', 'Vacant Housing', 'Percent Unemployed', 'Median Family Income'])
y_axis = st.selectbox(
    'Pick a Y-axis value:',
     ['Percent Unemployed','Gini Index', 'Vacant Housing','Median Family Income'])
sns.set()
plt.figure()
sns.set_style('darkgrid')
plt.title('Seaborn lmplot analysis by Income Quartile')
sns.set_context("paper", font_scale=1.3) 
sns.lmplot(x=x_axis, y=y_axis, data=df, hue='Income Quartile',col='Income Quartile',col_wrap=2)
st.pyplot()





