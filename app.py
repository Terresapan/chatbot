import streamlit as st
from graph_logic import setup_critique_graph
from langchain_groq import ChatGroq
from utils import save_feedback
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]["API_KEY"]
os.environ["LANGCHAIN_PROJECT"] = "Tagline_Generator"


# Enhanced Streamlit chatbot interface
st.sidebar.header("💬 Marketing Tagline Generator")
st.sidebar.markdown(
    "This app generates and critiques marketing taglines using LangGraph. "
    "To use this App, you need to provide a Groq API key, which you can get [here](https://console.groq.com/keys) for free.")
st.sidebar.write("### Instructions")
st.sidebar.write(":pencil: Enter your product or service description, target audience, and selling points.")
st.sidebar.write(":point_right: Click 'Generate Tagline' to receive tagline suggestions and a whole critique process.")
st.sidebar.write(":heart_decoration: Tell me your thoughts and feedback about the App.")

# Initialize session state for feedback storage if not already done
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""

# Feedback Form
st.sidebar.subheader("Feedback Form")
feedback = st.sidebar.text_area("Your Thoughts and Feedback", value=st.session_state.feedback, placeholder="Share your feedback here...")
    
if st.sidebar.button("Submit Feedback"):
    if feedback:
        try:
            save_feedback(feedback)
            st.session_state.feedback = ""  # Clear feedback after submission
            st.sidebar.success("Thank you for your feedback! 😊")
        except Exception as e:
            st.sidebar.error(f"Error saving feedback: {str(e)}")
    else:
        st.sidebar.error("Please enter your feedback before submitting.")

st.sidebar.image("assets/logo01.jpg", use_container_width=True)

# ask user for their OpenAI API key via `st.text_input`.
groq_api_key = st.text_input("Groq API Key", type="password", placeholder="Your Groq API Key here...")
if not groq_api_key:
    st.info("Please add your Groq API key to continue.", icon="🗝️")
else:
    # create an openai client
    model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.8, api_key=groq_api_key)

    # input field for user to input a product description
    st.header("Enter Product Details")
    product_description_input = st.text_input("Enter a Product/Service Description", placeholder="organic soup")
    target_audience_input = st.text_input("Enter the Target Audience", placeholder="for busy working adults")
    selling_point_input = st.text_input("Enter Key Selling Points", placeholder="ready in 5 minutes")

    # button to trigger tagline generation
    if st.button("Generate Tagline"):
        # Validate inputs
        if not product_description_input or not target_audience_input or not selling_point_input:
            st.error("Please fill out all fields to generate a tagline.", icon="🚫")
        else:
            # Set up the initial state (reflectionstate object)
            input_state = {"product_description": product_description_input,
                           "target_audience": target_audience_input,
                           "selling_point": selling_point_input,
                           "messages": []}
            # Setup graph and inject model
            critique_graph = setup_critique_graph(model)
            # Invoke the compiled debate graph
            messages = critique_graph.compile().invoke(input=input_state)
            # Display messages
            st.subheader("Generated Tagline")
            for m in messages["messages"]:
                st.write(f"🚨 AI: {m.content}")
