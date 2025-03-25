import streamlit as st
import requests
import json

# Function to call Groq API for take rate simulation
def simulate_take_rate(model1, model2, customer_group, market):
    api_url = "https://api.groq.com/simulate_take_rate"
    headers = {"Content-Type": "application/json", "Authorization": "Bearer YOUR_API_KEY"}
    
    payload = {
        "model1": model1,
        "model2": model2,
        "customer_group": customer_group,
        "market": market
    }
    
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response_data = response.json()
        return response_data.get("take_rate_model1", 50), response_data.get("take_rate_model2", 50)
    except Exception as e:
        st.error(f"Error fetching take rates: {e}")
        return 50, 50  # Default to 50-50 split in case of failure

customer_group_descriptions = {
    "Family First": "Families looking for spacious, safe, and cost-efficient EVs.",
    "Urban Single": "Young professionals in cities who value technology and design.",
    "Grey Hair": "Older buyers seeking comfort, safety, and reliability."
}

st.title("EV Model Take Rate Simulator")

# Sidebar for Customer Group and Market Selection
st.sidebar.header("Select Customer Group")
customer_group = st.sidebar.selectbox("Customer Group", list(customer_group_descriptions.keys()))
st.sidebar.write(f"**Description:** {customer_group_descriptions[customer_group]}")

st.sidebar.header("Select Market")
market = st.sidebar.selectbox("Market", ["Germany", "China", "US"])

# Columns for inputting two models
col1, col2 = st.columns(2)

with col1:
    st.subheader("Model 1")
    brand1 = st.selectbox("Brand", ["Tesla", "BYD", "Nio", "Xpeng", "Lucid"], key='brand1')
    bodytype1 = st.selectbox("Body Type", ["Sedan", "SUV"], key='body1')
    e_range1 = st.slider("Electric Range (km)", 100, 1500, 500, key='range1')
    price1 = st.slider("Price (k USD)", 20, 150, 50, key='price1')
    adas1 = st.selectbox("ADAS Level", ["L2", "L3", "L3+"], key='adas1')

with col2:
    st.subheader("Model 2")
    brand2 = st.selectbox("Brand", ["Tesla", "BYD", "Nio", "Xpeng", "Lucid"], key='brand2')
    bodytype2 = st.selectbox("Body Type", ["Sedan", "SUV"], key='body2')
    e_range2 = st.slider("Electric Range (km)", 100, 1500, 500, key='range2')
    price2 = st.slider("Price (k USD)", 20, 150, 50, key='price2')
    adas2 = st.selectbox("ADAS Level", ["L2", "L3", "L3+"], key='adas2')

if st.button("Simulate Take Rates"):
    model1 = {"brand": brand1, "bodytype": bodytype1, "electric_range": e_range1, "price": price1, "adas": adas1}
    model2 = {"brand": brand2, "bodytype": bodytype2, "electric_range": e_range2, "price": price2, "adas": adas2}
    take_rate1, take_rate2 = simulate_take_rate(model1, model2, customer_group, market)
    
    st.success(f"Take Rate for Model 1: {take_rate1}%")
    st.success(f"Take Rate for Model 2: {take_rate2}%")
    
    st.subheader("Simulation Results")
    st.bar_chart({"Model 1": take_rate1, "Model 2": take_rate2})
