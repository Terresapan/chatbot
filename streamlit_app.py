import streamlit as st
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, MessagesState, END

# Here is LangGraph logic
class ReflectionState(MessagesState):
    product_description: str
    target_audience: str
    selling_point: str

# Define the logic for each node
from langchain_core.messages import SystemMessage, HumanMessage
def generate_agent(state: ReflectionState):
    generate_prompt = """
    You are a marketing copy writer tasked with writing excellent product tagline. Respond with a revised version of your previous attempts if reflection_agent provides critique.
    Write a tagline for the given {product_description}, based on {target_audience} and {selling_point}. Revise your output based on {messages}.
    """
    prompt = generate_prompt.format(product_description=state["product_description"], target_audience=state["target_audience"], selling_point=state["selling_point"], messages=state["messages"])
    response = model.invoke(prompt)
    return {"messages": [{"role": "ai", "content": response.content}]}

def reflection_agent(state: ReflectionState):
    generate_prompt = """
    You are a marketing expert tasked with providing critiue for product tagling. Do not rewrite the tagline directly, but always provide recommendations, including requests for length, relevence, style, etc on how to improve.
    Provide recommendations on how to imporve the tagline for the given {product_description}, {target_audience}, and {selling_point} based on {messages}.
    """
    prompt = generate_prompt.format(product_description=state["product_description"], target_audience=state["target_audience"], selling_point=state["selling_point"], messages=state["messages"])
    response = model.invoke(prompt)
    return {"messages": [{"role": "ai", "content": response.content}]}


def should_loop(state: ReflectionState):
    if len(state['messages']) <= 4:
      return "reflection"
    return END

# Create the graph
debate_graph = StateGraph(ReflectionState)

# Add nodes
debate_graph.add_node("generate", generate_agent)
debate_graph.add_node("reflection", reflection_agent)

# Define edges
debate_graph.add_conditional_edges("generate", should_loop)
debate_graph.add_edge("reflection", "generate")

# Set entry point
debate_graph.set_entry_point("generate")

# Compile the graph
compiled_debate_graph = debate_graph.compile()

# Below is Streamlit Chatbot Interface

# Show title and description.
st.title("💬 Marketing Tagline Generator and Critique")
st.write(
    "This chatbot generates and self-critiques marketing taglines using LangGraph. To use this app, you need to provide a Groq API key, which you can get [here](https://console.groq.com/keys) for free. "
)

# Ask user for their OpenAI API key via `st.text_input`.
groq_api_key = st.text_input("Groq API Key", type="password")
if not groq_api_key:
    st.info("Please add your Groq API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    model = ChatGroq(model="llama-3.1-70b-versatile", temperature=0.7, api_key=groq_api_key)

    # Input field for user to input a product description
    product_description_input = st.text_input("Enter a product / service description (e.g., Organic soup)")
    target_audience_input = st.text_input("Enter the target audience (e.g., for working adults):")
    selling_point_input = st.text_input("Enter key selling points (e.g., Ready in 5 minutes):")

    # Button to trigger tagline generation
    if st.button("Generate Tagline") and product_description_input and target_audience_input and selling_point_input:
        # Set up the initial state (ReflectionState object)
        input = {"product_description": product_description_input, "target_audience": target_audience_input, "selling_point": selling_point_input}
        messages = compiled_debate_graph.invoke(input=input)
        for m in messages["messages"]:
            st.write(m.content)

