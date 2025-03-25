import streamlit as st
import os
import groq

# Load API Key securely from Streamlit secrets or environment variables
API_KEY = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else os.getenv("GROQ_API_KEY")

# Initialize Groq Client
os.environ["GROQ_API_KEY"] = api_key
client = groq.Client(api_key=API_KEY)

def get_take_rate(model1, model2, customer_group, market):
    """Fetch take rate simulation from Groq API using the client."""
    
    prompt = f"""
    Given the following EV models and market conditions, predict the take rate for each model.

    **Model 1:** {model1}
    **Model 2:** {model2}
    **Customer Group:** {customer_group}
    **Market:** {market}

    Return the take rates as percentages summing to 100%.
    """

    response = client.chat.completions.create(
        model="mixtral-8x7b",  # Adjust model based on Groq's available models
        messages=[
            {"role": "system", "content": "You are an expert in EV market analysis."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    take_rates = response.choices[0].message.content
    return parse_take_rates(take_rates)  # Function to extract numbers from response

def parse_take_rates(response_text):
    """Extracts numerical take rates from the response."""
    import re
    matches = re.findall(r"(\d+)", response_text)
    if len(matches) >= 2:
        return int(matches[0]), int(matches[1])
    return None, None

# Streamlit UI
st.title("EV Model Take Rate Simulator")

# Sidebar inputs
st.sidebar.header("Select Customer Group")
customer_group = st.sidebar.selectbox("Customer Group", ["Family First", "Urban Single", "Grey Hair"])
st.sidebar.header("Select Market")
market = st.sidebar.selectbox("Market", ["Germany", "China", "US"])

# Columns for models
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
    
    take_rate1, take_rate2 = get_take_rate(model1, model2, customer_group, market)
    
    if take_rate1 is not None and take_rate2 is not None:
        st.success(f"Take Rate for Model 1: {take_rate1}%")
        st.success(f"Take Rate for Model 2: {take_rate2}%")
        st.bar_chart({"Model 1": take_rate1, "Model 2": take_rate2})
