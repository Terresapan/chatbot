from langgraph.graph import StateGraph, MessagesState, END

# Define reflection state
class reflectionstate(MessagesState):
    product_description: str
    target_audience: str
    selling_point: str

# Generate agent logic
def generate_agent(state: reflectionstate, model):
    generate_prompt = """
    You are a marketing copywriter tasked with writing an excellent product tagline. Respond with a revised version of your previous attempts if the reflection_agent provides critique.
    Write a tagline for the given {product_description}, based on {target_audience} and {selling_point}. Revise your output based on {messages}.
    """
    prompt = generate_prompt.format(
        product_description=state["product_description"],
        target_audience=state["target_audience"],
        selling_point=state["selling_point"],
        messages=state["messages"]
    )
    try:
        response = model.invoke(prompt)
        return {"messages": [{"role": "ai", "content": response.content}]}
    except Exception as e:
        return {"messages": [{"role": "ai", "content": f"Error generating tagline: {str(e)}"}]}

# Reflection agent logic
def reflection_agent(state: reflectionstate, model):
    generate_prompt = """
    You are a marketing expert tasked with providing critique for product taglines. Provide recommendations on how to improve the tagline for the given {product_description}, {target_audience}, and {selling_point} based on {messages}.
    """
    prompt = generate_prompt.format(
        product_description=state["product_description"],
        target_audience=state["target_audience"],
        selling_point=state["selling_point"],
        messages=state["messages"]
    )
    try:
        response = model.invoke(prompt)
        return {"messages": [{"role": "ai", "content": response.content}]}
    except Exception as e:
        return {"messages": [{"role": "ai", "content": f"Error generating critique: {str(e)}"}]}

# Loop condition logic
def should_loop(state: reflectionstate):
    return "reflection" if len(state['messages']) <= 4 else END


# Graph setup
def setup_critique_graph(model):
    critique_graph = StateGraph(reflectionstate)

    # Directly set up the nodes with a wrapper or pass the model differently
    critique_graph.add_node("generate", lambda state: generate_agent(state, model))
    critique_graph.add_node("reflection", lambda state: reflection_agent(state, model))

    critique_graph.add_conditional_edges("generate", should_loop)
    critique_graph.add_edge("reflection", "generate")

    critique_graph.set_entry_point("generate")
    return critique_graph