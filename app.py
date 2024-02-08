import streamlit as st
import pymongo
import pandas as pd
import os

store = st.secrets["URL"]
client = pymongo.MongoClient(store)
db = client["ibapiii"]
collection = db["ibapiii"]
# Function to get distinct options for a given field
st.set_page_config(layout="wide")

# Custom CSS to reduce button size
st.markdown("""
    <style>
        .stButton>button {
            width: 100px; /* Adjust width as needed */
            height: 10px; /* Adjust height as needed */
            font-size: 5px; /* Adjust font size as needed */
        }
    </style>
""", unsafe_allow_html=True)

def get_distinct_options(field):
    pipeline = [
        {"$match": {field: {"$ne": None}}},
        {"$group": {"_id": f"${field}"}},
        {"$sort": {"_id": 1}}
    ]
    distinct_options = collection.aggregate(pipeline)
    options_list = [option["_id"] for option in distinct_options]
    options_list.insert(0, 'All')
    return options_list

st.title("Ibapi")

col1, col2, col3, col4 = st.columns(4)

with col1:
    option1 = st.selectbox('State?', get_distinct_options("State"), key='state_selectbox')
    st.write('You selected:', option1)
    option = st.selectbox('Property subtype?', get_distinct_options("Property Sub Type"), key='property_subtype_selectbox')
    st.write('You selected:', option)
    option4 = st.selectbox('Bank Name?', get_distinct_options("Bank Name"), key='bank_name_selectbox')
    st.write('You selected:', option4)

with col2:
    option2 = st.selectbox('City?', get_distinct_options("City"), key='city_selectbox')
    st.write('You selected:', option2)

with col3:
    option3 = st.selectbox('District?', get_distinct_options("District"), key='district_selectbox')
    st.write('You selected:', option3)

def fetch_data(query={}):
    cursor = collection.find(query, {"_id": 0})
    df = pd.DataFrame(list(cursor))
    return df

query = {}
if option != 'All':
    query["Property Sub Type"] = option
if option1 != 'All':
    query["State"] = option1
if option2 != 'All':
    query["City"] = option2
if option3 != 'All':
    query["District"] = option3
if option4 != 'All':
    query["Bank Name"] = option4

data = fetch_data(query)

if not data.empty:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.write('Property Id')
    with col2:
        st.write('State')
    with col3:
        st.write('District')
    with col4:
        st.write('City')
    with col5:
        st.write('Button')
    for index, row in data.iterrows():
        with col1:
            st.write(index)
        with col2:
            st.write(row['State'])
        with col3:
            st.write(row['District'])
        with col4:
            st.write(row['City'])
        with col5:
            if st.button(f'Button {index}'):
                img = row['Images']
                try:
                    individual_urls = img.split(", ")
                    for url in individual_urls:
                        st.image(url, width=200) 
                except:
                    st.image(img, width=200)

else:               
    st.write("No data available for the selected filters.")
