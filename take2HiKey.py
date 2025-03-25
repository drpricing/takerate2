import streamlit as st
import os
import groq

# Function to format reasoning text
def format_reasoning(reasoning_text):
    """Formats the reasoning text for better readability."""
    formatted_text = reasoning_text.replace("**", "###").replace("*", "-")
    return formatted_text

# Function to handle Groq client initialization and take rate simulation
def get_take_rate(model1, model2, customer_group, market, api_key):
    """Fetch take rate simulation from Groq API."""
    try:
        # Initialize Groq Client with user-provided API key
        client = groq.Client(api_key=api_key)
        
        # Construct the prompt for the Groq model
        prompt = f"""
        Given the following EV models and market conditions, predict the take rate for each model.
        **Model 1:**
        Brand: {model1['brand']}
        Body Type: {model1['bodytype']}
        Electric Range: {model1['electric_range']} km
        Price: {model1['price']} k USD
        ADAS Level: {model1['adas']}
        
        **Model 2:**
        Brand: {model2['brand']}
        Body Type: {model2['bodytype']}
        Electric Range: {model2['electric_range']} km
        Price: {model2['price']} k USD
        ADAS Level: {model1['adas']}
        
        **Customer Group:** {customer_group}
        **Market:** {market}
        Consider the preferences and characteristics of the specified customer group and market when predicting the take rates.
        Return the take rates as percentages summing to 100%.
        """
        
        # Use the correct method to make a query to Groq
        response = client.chat.completions.create(
            model="llama3-70b-8192", # Adjust model name if needed
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        # Convert the response object to a dictionary
        response_dict = response.model_dump()
        
        # Parse the response from Groq and extract the take rates and reasoning
        take_rates = response_dict['choices'][0]['message']['content']
        reasoning = response_dict['choices'][0]['message']['content']
        take_rate1, take_rate2 = parse_take_rates(take_rates)
        
        # Validate and normalize take rates
        if take_rate1 is not None and take_rate2 is not None:
            total = take_rate1 + take_rate2
            if total != 100:
                take_rate1 = (take_rate1 / total) * 100
                take_rate2 = (take_rate2 / total) * 100
        
        return take_rate1, take_rate2, reasoning
    
    except Exception as e:
        st.error(f"Error with Groq API: {str(e)}")
        return None, None, None

# Function to extract numerical take rates from the Groq API response
def parse_take_rates(response_text):
    """Extracts numerical take rates from API response text."""
    import re
    matches = re.findall(r"(\d+)%", response_text)
    if len(matches) >= 2:
        return int(matches[0]), int(matches[1])
    return None, None

# Streamlit App UI
st.title("EV Model Take Rate Simulator")

# Read API key from secrets
api_key = st.secrets["groq"]["api_key"]

# Sidebar inputs for customer group and market
st.sidebar.header("Select Customer Group")
customer_group = st.sidebar.selectbox("Customer Group", ["Family First", "Urban Single", "Grey Hair"])
st.sidebar.header("Select Market")
market = st.sidebar.selectbox("Market", ["Germany", "China", "US"])

# Columns for selecting EV models
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

# Simulate take rates when button is clicked
if st.button("Simulate Take Rates"):
    if api_key:
        # Gather model input values
        model1 = {"brand": brand1, "bodytype": bodytype1, "electric_range": e_range1, "price": price1, "adas": adas1}
        model2 = {"brand": brand2, "bodytype": bodytype2, "electric_range": e_range2, "price": price2, "adas": adas2}
        
        # Get take rates from the Groq API
        take_rate1, take_rate2, reasoning = get_take_rate(model1, model2, customer_group, market, api_key)
        
        # Display results
        if take_rate1 is not None and take_rate2 is not None:
            st.success(f"Take Rate for Model 1: {take_rate1:.2f}%")
            st.success(f"Take Rate for Model 2: {take_rate2:.2f}%")
            st.bar_chart({"Model 1": take_rate1, "Model 2": take_rate2})
            
            # Format and display reasoning
            st.markdown("### Reasoning")
            formatted_reasoning = format_reasoning(reasoning)
            st.markdown(formatted_reasoning)
        else:
            st.warning("Please enter your API key to simulate take rates.")
