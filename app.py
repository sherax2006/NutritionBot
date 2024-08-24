
import requests
import streamlit as st
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables 
api_key = st.secrets["general"]["API_KEY"]
# Function to get Access Token
def get_access_token(api_key):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception("Error obtaining access token: " + response.text)

# Function to get nutrition recommendations
def get_nutrition_recommendation(user_input, access_token):
    access_token = get_access_token(api_key) 
    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    body = {
        "input": f"""Nutrition Bot

Input: {user_input}
Output:""",
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 300,
            "repetition_penalty": 1 
        },
        "model_id": "ibm/granite-13b-chat-v2",
        "project_id": "0ea78626-771d-4791-9ed1-67b0af498daa",
        "moderations": {
            "hap": {
                "input": {
                    "enabled": True,
                    "threshold": 0.6,
                    "mask": {
                        "remove_entity_value": True
                    }
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.6,
                    "mask": {
                        "remove_entity_value": True
                    }
                }
            }
        }
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        st.error("An error occurred: " + response.text)
        return None

    data = response.json()
    return data['results'][0]['generated_text']

# Function to check if input is nutrition-related
def is_nutrition_query(user_input):
    keywords = [
         "diet", "nutrition", "calorie", "vitamin", "mineral", "protein", "who are you"
         "carbohydrate", "fat", "meal plan", "supplement", "weight loss", 
         "healthy eating", "vegetables", "fruits", "hydration",'routine','workout','plan','Diet', 'Nutrition', 'Calorie', 'Vitamin', 'Mineral', 'Protein', 'Carbohydrate', 'Fat', 'Meal plan', 'Supplement', 'Weight loss', 'Healthy eating', 'Vegetables', 'Fruits', 'Hydration', 'Macronutrients', 'Micronutrients', 'Fiber', 'Cholesterol', 'Antioxidants', 'Omega-3', 'Sugar', 'Sodium', 'Potassium', 'Iron', 'Calcium', 'Zinc', 'Magnesium', 'Dietary', 'Food pyramid', 'Balanced diet', 'Organic', 'Gluten-free', 'Vegan', 'Vegetarian', 'Keto', 'Paleo', 'Intermittent fasting', 'Low-carb', 'Whole grains', 'Processed foods', 'Superfoods', 'Metabolism', 'Blood sugar', 'Glycemic index', 'BMR', 'BMI', 'Energy intake', 'Portion control', 'Eating habits'
     ]
    return any(keyword in user_input.lower() for keyword in keywords)

# Function to check if input is valid
def is_valid_input(user_input):
    # Check if input contains at least one alphabet character
    return bool(re.search('[a-zA-Z]', user_input))

# Streamlit UI
st.set_page_config(page_title="Nutrition Bot", layout="centered")

# Add custom CSS for background color and styles
st.markdown("""
    <style>
    .main {
        background-color: #f7f9fc;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
    }
    .title {
        color:#003166; /* Title color */
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center;
    }
    .error-message {
        color: #FF4B4B;
        font-size: 18px;
        font-weight: bold;
        margin-top: 10px;
    }
    .recommendation-title {
        color: #007BFF;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .recommendation-content {
        color: #333;
        font-size: 18px;
        line-height: 1.6;
        
    }
    .highlight {
        background-color: #e8f5e9;
        padding: 10px;
        border-left: 4px solid #4CAF50;
        margin-bottom: 20px;
    }
    ul {
        list-style-type: none;
        margin-left: 0;
        padding-left: 0;
        color: #333;
        font-size: 18px;
        line-height: 1.6;
    }
    li::before {
        content: "• ";
        color: #4CAF50;
        font-size: 24px;
        font-weight: bold;
        margin-right: 10px;
    }
    .bullet-title {
        font-weight: bold;
        font-size: 20px;
        color: #333;
        margin-bottom: 5px;
    }
    .prompt-button {
        background-color: #007BFF;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        margin: 10px;
        cursor: pointer;
        text-decoration: none;
        text-align: center;
        display: inline-block;
        background:#003166;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main">', unsafe_allow_html=True)

st.markdown('<div class="title">Nutrition Bot</div>', unsafe_allow_html=True)
st.subheader("Get personalized nutrition recommendations to help you maintain a healthy lifestyle.")

st.markdown("### How It Works:")
st.markdown("""
<ul>
<li><span class="bullet-title">Enter Your Query:</span> Enter your question or concern about nutrition in details into the input box.</li>
<li><span class="bullet-title">Click "Get Recommendation":</span> Hit the button to submit your query.</li>
<li><span class="bullet-title">Receive Your Advice:</span> Get tailored nutrition advice directly based on your input.</li>
</ul>
""", unsafe_allow_html=True)

# Initialize a session state to keep track of user input
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Display input text box with previous search value
user_input = st.text_input("Enter your query:", value=st.session_state.user_input, placeholder="What is the best diet for weight loss?")

# Update session state with the latest input
st.session_state.user_input = user_input

# Display the recommendation when the user submits the input
if st.button("Get Recommendation"):
    if not user_input.strip():
        st.markdown('<p class="error-message">Please enter a valid query. Empty input is not allowed!</p>', unsafe_allow_html=True)
    elif not is_valid_input(user_input):
        st.markdown('<p class="error-message">Invalid input! Please enter text that includes letters. Numbers or special characters alone are not allowed!</p>', unsafe_allow_html=True)
    elif not is_nutrition_query(user_input):
        st.markdown('<p class="error-message">This bot only responds to nutrition-related queries. Please ask a nutrition-related question.</p>', unsafe_allow_html=True)
    else:
        access_token = st.secrets["general"]["IBM_ACCESS_TOKEN"]  # Use the access token from Streamlit secrets
        with st.spinner("Generating recommendation..."):
            recommendation = get_nutrition_recommendation(user_input, access_token)
            if recommendation:
                if recommendation.strip():  # Check if the recommendation is not empty or whitespace
                    st.markdown('<div class="recommendation-title">Nutrition Recommendation:</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="highlight"><div class="recommendation-content">{recommendation}</div></div>', unsafe_allow_html=True)
                else:
                    st.info("Can't find any diet plan based on the provided input.")
            else:
                st.info("Can't find any diet plan based on the provided input. Please try again with a different query.")

# Define prompts
prompts = [
    "Best diet for weight loss",
    "Nutrition tips for athletes",
    "Healthy meal plans",
    "Supplements guide",
    "Importance of hydration",
    "Benefits of fruits and vegetables",
    "Protein-rich diet benefits",
    "Guide to vitamins and minerals",
    "Carbohydrates and their role",
    "Fat: myths and facts"
]

# Display clickable prompts
st.markdown("### Or Choose a Prompt:")
for prompt in prompts:
    if st.button(prompt, key=f"prompt_{prompt}"):  # Use the prompt as a unique key
        access_token = st.secrets["general"]["IBM_ACCESS_TOKEN"]
        user_input = prompt  # Use the prompt as the user input
        with st.spinner("Generating recommendation..."):
            recommendation = get_nutrition_recommendation(user_input, access_token)
            if recommendation:
                if recommendation.strip():
                    st.markdown('<div class="recommendation-title">Nutrition Recommendation:</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="highlight"><div class="recommendation-content">{recommendation}</div></div>', unsafe_allow_html=True)
                else:
                    st.info("Can't find any diet plan based on the provided input.")
            else:
                st.info("Can't find any diet plan based on the provided input. Please try again with a different query.")

# Footer
st.markdown("""
    <style>
        footer {visibility: hidden;}
        .footer {
            visibility: visible;
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f1f1f1;
            color: black;
            text-align: center;
            padding: 10px;
        }
    </style>
    <div class="footer">
        <p>Powered by IBM Watson | Developed by M Sheraz Rana</p>
    </div>
""", unsafe_allow_html=True)

# Disclaimer for serious patients
st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <strong>Disclaimer:</strong> The nutrition advice provided by this bot is for informational and research purposes. Serious patients should consult a doctor for personalized medical advice.
    </div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
