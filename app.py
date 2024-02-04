import streamlit as st
import pymongo
import pandas as pd

store = URL
client = pymongo.MongoClient(store)
db = client["ibapiii"]
collection = db["ibapi"]

pipeline = [
    {"$match": {"Property Sub Type": {"$ne": None}}},
    {"$group": {"_id": "$Property Sub Type"}},
    {"$sort": {"_id": 1}}
]
distinct_options = collection.aggregate(pipeline)
options_list = [option["_id"] for option in distinct_options]
options_list.insert(0, 'All')

st.title("Data Viewer")

def fetch_data(query={}):
    cursor = collection.find(query, {"_id": 0}) 
    df = pd.DataFrame(list(cursor))  
    return df

option = st.selectbox(
    'How would you like to be contacted?',
    options_list
)
st.write('You selected:', option)

if option == 'All':
    data = fetch_data()
else:
    data = fetch_data({"Property Sub Type": option})

st.write(data)
