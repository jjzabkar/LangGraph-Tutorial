from langgraph.graph import StateGraph, START, END

from src.agents import State
from src.agents.logical_agent_node import logical_agent_node
from src.agents.message_classifier_node import message_classifier_node
from src.agents.music_agent_node import music_agent_node
from src.agents.router_node import router_node
from src.agents.therapist_agent_node import therapist_agent_node

CLASSIFIER_NODE = "classifier_node"
ROUTER_NODE = "router_node"
THERAPIST_AGENT_NODE = "therapist_agent_node"
LOGICAL_AGENT_NODE = "logical_agent_node"
MUSIC_AGENT_NODE = "music_agent_node"

graph_builder = StateGraph(State)
graph_builder.add_node(CLASSIFIER_NODE, message_classifier_node)
graph_builder.add_node(ROUTER_NODE, router_node)
graph_builder.add_node(THERAPIST_AGENT_NODE, therapist_agent_node)
graph_builder.add_node(LOGICAL_AGENT_NODE, logical_agent_node)
graph_builder.add_node(MUSIC_AGENT_NODE, music_agent_node)

graph_builder.add_edge(START, CLASSIFIER_NODE)
graph_builder.add_edge(CLASSIFIER_NODE, ROUTER_NODE)


graph_builder.add_conditional_edges(
    ROUTER_NODE,
    lambda state: state.get("next"),
    {"therapist": THERAPIST_AGENT_NODE, "logical": LOGICAL_AGENT_NODE, "music": MUSIC_AGENT_NODE}
)

graph_builder.add_edge(THERAPIST_AGENT_NODE, END)
graph_builder.add_edge(LOGICAL_AGENT_NODE, END)
graph_builder.add_edge(MUSIC_AGENT_NODE, END)

my_graph = graph_builder.compile()






graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {"therapist": "therapist", "logical": "logical", "music": "music"}
)