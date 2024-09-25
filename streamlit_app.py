import streamlit as st
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, MessagesState, END

# here is langgraph logic
class reflectionstate(MessagesState):
    product_description: str
    target_audience: str
    selling_point: str

# define the logic for each node
def generate_agent(state: reflectionstate):
    generate_prompt = """
    You are a marketing copywriter tasked with writing an excellent product tagline. Respond with a revised version of your previous attempts if the reflection_agent provides critique.
    Write a tagline for the given {product_description}, based on {target_audience} and {selling_point}. Revise your output based on {messages}.
    """
    prompt = generate_prompt.format(product_description=state["product_description"],
                                     target_audience=state["target_audience"],
                                     selling_point=state["selling_point"],
                                     messages=state["messages"])

    try:
        response = model.invoke(prompt)
        return {"messages": [{"role": "ai", "content": response.content}]}
    except Exception as e:
        return {"messages": [{"role": "ai", "content": f"Error generating tagline: {str(e)}"}]}

def reflection_agent(state: reflectionstate):
    generate_prompt = """
    You are a marketing expert tasked with providing critique for product taglines. Do not rewrite the tagline directly, but always provide recommendations, including requests for length, relevance, style, etc. on how to improve.
    Provide recommendations on how to improve the tagline for the given {product_description}, {target_audience}, and {selling_point} based on {messages}.
    """
    prompt = generate_prompt.format(product_description=state["product_description"],
                                     target_audience=state["target_audience"],
                                     selling_point=state["selling_point"],
                                     messages=state["messages"])

    try:
        response = model.invoke(prompt)
        return {"messages": [{"role": "ai", "content": response.content}]}
    except Exception as e:
        return {"messages": [{"role": "ai", "content": f"Error generating critique: {str(e)}"}]}

def should_loop(state: reflectionstate):
    return "reflection" if len(state['messages']) <= 4 else END

# create the graph
debate_graph = StateGraph(reflectionstate)

# add nodes
debate_graph.add_node("generate", generate_agent)
debate_graph.add_node("reflection", reflection_agent)

# define edges
debate_graph.add_conditional_edges("generate", should_loop)
debate_graph.add_edge("reflection", "generate")

# set entry point
debate_graph.set_entry_point("generate")

# compile the graph
compiled_debate_graph = debate_graph.compile()

# Enhanced Streamlit chatbot interface
st.sidebar.header("💬 Marketing Tagline Generator")
st.sidebar.markdown("This app generates and critiques marketing taglines. To use this App, you need to provide a Groq API key, which you can get [here](https://console.groq.com/keys) for free.")
st.sidebar.write("### Instructions")
st.sidebar.write(":spiral_note_pad: Enter your product or service description, target audience, and selling points.")
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
        st.sidebar.success("Thank you for your feedback! 😊")

        # Store feedback to a text file
        try:
            feedback_file_path = "/workspaces/chatbot/feedback.txt"
            with open(feedback_file_path, "a") as feedback_file:
                feedback_file.write(feedback + "\n")  # Append feedback with a newline
            st.session_state.feedback = ""  # Clear feedback after submission
        except Exception as e:
            st.sidebar.error(f"Error saving feedback: {str(e)}")
    else:
        st.sidebar.error("Please enter your feedback before submitting.")

st.sidebar.image("assets/icon01.png", use_column_width=True)

# ask user for their OpenAI API key via `st.text_input`.
groq_api_key = st.text_input("Groq API Key", type="password")
if not groq_api_key:
    st.info("Please add your Groq API key to continue.", icon="🗝️")
else:
    # create an openai client
    model = ChatGroq(model="llama-3.1-70b-versatile", temperature=0.7, api_key=groq_api_key)

    # input field for user to input a product description
    st.header("Enter Product Details")
    product_description_input = st.text_input("Enter a Product/Service Description (e.g., organic soup)")
    target_audience_input = st.text_input("Enter the Target Audience (e.g., for working adults):")
    selling_point_input = st.text_input("Enter Key Selling Points (e.g., ready in 5 minutes):")

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

            # Invoke the compiled debate graph
            messages = compiled_debate_graph.invoke(input=input_state)
            # Display messages
            st.subheader("Generated Tagline")
            for m in messages["messages"]:
                st.write(f"🚨 AI: {m.content}")
