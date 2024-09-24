import streamlit as st
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, END

# Here is LangGraph logic
class ReflectionState(MessagesState):
    product: str

def generate_agent(state: ReflectionState):
    generate_prompt = """
    You are a marketing copywriter tasked with writing an excellent product tagline. Respond with a revised version of your previous attempts if reflection_agent provides critique.
    Write a tagline for the given {product}. Revise your output based on {messages}.
    """
    prompt = generate_prompt.format(product=state["product"], messages=state["messages"])
    response = model.invoke(prompt)
    return {"messages": [{"role": "assistant", "content": response.content}]}

def reflection_agent(state: ReflectionState):
    generate_prompt = """
    You are a marketing expert tasked with providing critique for a product tagline. Do not rewrite the tagline directly, but always provide recommendations, including requests for length, relevance, style, etc., on how to improve.
    Provide recommendations on how to improve the tagline for the given {product} based on {messages}.
    """
    prompt = generate_prompt.format(product=state["product"], messages=state["messages"])
    response = model.invoke(prompt)
    return {"messages": [{"role": "assistant", "content": response.content}]}

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
    "This chatbot generates and critiques marketing taglines using LangGraph. To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=openai_api_key)

    # Input field for user to input a product description
    product_input = st.text_input("Enter a product description (e.g., Organic soup for busy working adults):")

    # Button to trigger tagline generation
    if st.button("Generate Tagline") and product_input:
        # Set up the initial state (ReflectionState object)
        input = {"product": product_input}
        messages = compiled_debate_graph.invoke(input)

        for m in messages['messages']:
            st.write(m.content)

