from langgraph.graph import StateGraph, START, END

from src.agents import State
from src.agents.logical_agent_node import logical_agent_node
from src.agents.message_classifier_node import message_classifier_node
from src.agents.router_node import router_node
from src.agents.therapist_agent_node import therapist_agent_node
from langgraph.graph import StateGraph, START, END

from src.agents import State
from src.agents.logical_agent_node import logical_agent_node
from src.agents.message_classifier_node import message_classifier_node
from src.agents.router_node import router_node
from src.agents.therapist_agent_node import therapist_agent_node


graph_builder = StateGraph(State)
graph_builder.add_node("classifier", message_classifier_node)
graph_builder.add_node("router", router_node)
graph_builder.add_node("therapist", therapist_agent_node)
graph_builder.add_node("logical", logical_agent_node)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {"therapist": "therapist", "logical": "logical"}
)

graph_builder.add_edge("therapist", END)
graph_builder.add_edge("logical", END)

my_graph = graph_builder.compile()
