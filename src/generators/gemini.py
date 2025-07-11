from flask import Flask, Response, request, jsonify
from langgraph.graph import StateGraph, END
import asyncio
import time
import json
import uuid
from typing import AsyncGenerator, List, Any, Dict, Union

app = Flask(__name__)


# --- LangGraph Graph Definition ---

class GraphState:
    """Represents the state of our graph."""

    def __init__(self, customer_input: str = "", decisions: List[str] = None, updates: List[str] = None,
                 final_content: str = None):
        self.customer_input = customer_input
        self.decisions = decisions if decisions is not None else []
        self.updates = updates if updates is not None else []
        self.final_content = final_content


# Define schemas for output
class ThinkingSchema:
    def __init__(self, node_name: str, status: str, message: str, step_id: str):
        self.node_name = node_name
        self.status = status
        self.message = message
        self.step_id = step_id

    def to_json(self) -> str:
        return json.dumps({
            "type": "thinking",
            "node_name": self.node_name,
            "status": self.status,
            "message": self.message,
            "step_id": self.step_id
        })


class ContentSchema:
    def __init__(self, content_type: str, data: Any, step_id: str):
        self.content_type = content_type
        self.data = data
        self.step_id = step_id

    def to_json(self) -> str:
        return json.dumps({
            "type": "content",
            "content_type": self.content_type,
            "data": self.data,
            "step_id": self.step_id
        })


# Generator functions for output
def generate_thinking_output(node_name: str, status: str, message: str) -> AsyncGenerator[str, None]:
    step_id = str(uuid.uuid4())
    yield ThinkingSchema(node_name, status, message, step_id).to_json() + "\n"


def generate_content_output(content_type: str, data: Any) -> AsyncGenerator[str, None]:
    step_id = str(uuid.uuid4())
    yield ContentSchema(content_type, data, step_id).to_json() + "\n"


async def decision_node(state: GraphState) -> AsyncGenerator[Union[GraphState, str], None]:
    node_name = "DecisionMaker"
    async for output in generate_thinking_output(node_name, "processing", "Analyzing customer input..."):
        yield output

    await asyncio.sleep(1)  # Simulate quick processing

    customer_input = state.customer_input.lower()
    decision_made = "default_path"

    if "product" in customer_input:
        decision_made = "product_inquiry"
    elif "support" in customer_input:
        decision_made = "support_request"
    elif "pricing" in customer_input:
        decision_made = "pricing_info"

    async for output in generate_thinking_output(node_name, "completed", f"Decision made: {decision_made}"):
        yield output

    state.decisions.append(decision_made)
    yield state


async def product_inquiry_node(state: GraphState) -> AsyncGenerator[Union[GraphState, str], None]:
    node_name = "ProductInquiryProcessor"
    async for output in generate_thinking_output(node_name, "processing", "Gathering product information..."):
        yield output

    await asyncio.sleep(5)  # Simulate long-running task

    product_data = {
        "name": "SuperWidget 5000",
        "features": ["Feature A", "Feature B", "Feature C"],
        "price": "$99.99"
    }

    async for output in generate_thinking_output(node_name, "completed", "Product information retrieved."):
        yield output
    async for output in generate_content_output("product_details", product_data):
        yield output
    yield state


async def support_request_node(state: GraphState) -> AsyncGenerator[Union[GraphState, str], None]:
    node_name = "SupportRequestProcessor"
    async for output in generate_thinking_output(node_name, "processing", "Escalating to support team..."):
        yield output

    await asyncio.sleep(5)  # Simulate long-running task

    ticket_id = f"SR-{int(time.time())}"
    support_message = f"Your support request has been logged. Your ticket ID is {ticket_id}. A support agent will contact you shortly."

    async for output in generate_thinking_output(node_name, "completed", "Support request processed."):
        yield output
    async for output in generate_content_output("support_confirmation",
                                                {"message": support_message, "ticket_id": ticket_id}):
        yield output
    yield state


async def pricing_info_node(state: GraphState) -> AsyncGenerator[Union[GraphState, str], None]:
    node_name = "PricingInformationProvider"
    async for output in generate_thinking_output(node_name, "processing", "Fetching latest pricing details..."):
        yield output

    await asyncio.sleep(5)  # Simulate long-running task

    pricing_details = {
        "basic": "$10/month",
        "premium": "$25/month",
        "enterprise": "Contact sales"
    }

    async for output in generate_thinking_output(node_name, "completed", "Pricing information fetched."):
        yield output
    async for output in generate_content_output("pricing_table", pricing_details):
        yield output
    yield state


async def default_response_node(state: GraphState) -> AsyncGenerator[Union[GraphState, str], None]:
    node_name = "DefaultResponder"
    async for output in generate_thinking_output(node_name, "processing", "Preparing a general response..."):
        yield output

    await asyncio.sleep(2)  # Simulate some processing

    general_message = "Thank you for your inquiry. Please provide more details so I can assist you better, or choose from options like 'product', 'support', or 'pricing'."

    async for output in generate_thinking_output(node_name, "completed", "General response prepared."):
        yield output
    async for output in generate_content_output("general_message", general_message):
        yield output
    yield state


# Build the LangGraph graph
workflow = StateGraph(GraphState)

workflow.add_node("decision", decision_node)
workflow.add_node("product_inquiry", product_inquiry_node)
workflow.add_node("support_request", support_request_node)
workflow.add_node("pricing_info", pricing_info_node)
workflow.add_node("default_response", default_response_node)

workflow.set_entry_point("decision")

workflow.add_conditional_edges(
    "decision",
    lambda state: state.decisions[-1] if state.decisions else "default_path",
    {
        "product_inquiry": "product_inquiry",
        "support_request": "support_request",
        "pricing_info": "pricing_info",
        "default_path": "default_response"
    },
)

workflow.add_edge("product_inquiry", END)
workflow.add_edge("support_request", END)
workflow.add_edge("pricing_info", END)
workflow.add_edge("default_response", END)

# Compile the graph
graph = workflow.compile()


# --- Flask Application ---

@app.route('/invoke_graph', methods=['GET'])
async def invoke_graph() -> Response:
    customer_input = request.args.get('input', '')

    async def generate() -> AsyncGenerator[str, None]:
        initial_state = GraphState(customer_input=customer_input)
        async for s in graph.astream(initial_state):
            for key, value in s.items():
                if isinstance(value, GraphState):
                    # In a real scenario, you'd extract relevant information from the state
                    # that you want to send as a "thinking" update or content.
                    # For this example, the nodes themselves are yielding the JSON.
                    pass
                elif isinstance(value, str):
                    # Directly yield the JSON string from the generator nodes
                    yield value
                elif isinstance(value, dict) and "customer_input" in value:
                    # Initial state will be yielded as a dict, we can ignore it for direct output
                    pass
                else:
                    # Handle other potential outputs from nodes if necessary
                    # print(f"Unhandled output type: {type(value)}: {value}")
                    pass

    return Response(generate(), mimetype='application/json-stream')


if __name__ == '__main__':
    # To run this Flask app:
    # 1. Save the code as a Python file (e.g., app.py).
    # 2. Install necessary libraries: pip install Flask langgraph asyncio
    # 3. Run from your terminal: python -m flask --app app run
    #    (For development, you might want to add --debug for auto-reloading)
    #
    # Then access in your browser or with curl:
    # curl -N "http://127.0.0.1:5000/invoke_graph?input=I need product info"
    # curl -N "http://127.0.0.1:5000/invoke_graph?input=I have a support issue"
    # curl -N "http://127.00.1:5000/invoke_graph?input=What's the pricing?"
    # curl -N "http://127.0.0.1:5000/invoke_graph?input=Hello"
    app.run(debug=True, use_reloader=False)  # use_reloader=False because astream might have issues with reloader
