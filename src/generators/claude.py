from flask import Flask, request, Response, jsonify
import json
import time
import asyncio
from typing import Dict, Any, Generator, TypedDict, Literal
from dataclasses import dataclass
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor


# LangGraph-like implementation
class StateGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.entry_point = None
        self.finish_point = "END"

    def add_node(self, name: str, func):
        self.nodes[name] = func
        return self

    def add_edge(self, from_node: str, to_node: str):
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(to_node)
        return self

    def add_conditional_edges(self, from_node: str, condition_func, mapping: Dict[str, str]):
        self.edges[from_node] = {"conditional": True, "func": condition_func, "mapping": mapping}
        return self

    def set_entry_point(self, node_name: str):
        self.entry_point = node_name
        return self

    def compile(self):
        return CompiledGraph(self.nodes, self.edges, self.entry_point, self.finish_point)


class CompiledGraph:
    def __init__(self, nodes, edges, entry_point, finish_point):
        self.nodes = nodes
        self.edges = edges
        self.entry_point = entry_point
        self.finish_point = finish_point

    def stream(self, state: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        current_node = self.entry_point

        while current_node != self.finish_point:
            if current_node not in self.nodes:
                break

            # Execute the current node
            node_func = self.nodes[current_node]
            for result in node_func(state):
                yield result

            # Determine next node
            if current_node in self.edges:
                edge_config = self.edges[current_node]

                if isinstance(edge_config, dict) and edge_config.get("conditional"):
                    # Conditional edge
                    condition_result = edge_config["func"](state)
                    current_node = edge_config["mapping"].get(condition_result, self.finish_point)
                elif isinstance(edge_config, list) and len(edge_config) > 0:
                    # Direct edge
                    current_node = edge_config[0]
                else:
                    current_node = self.finish_point
            else:
                current_node = self.finish_point


# Schemas for responses
class ResponseType(Enum):
    THINKING = "thinking"
    CONTENT = "content"


@dataclass
class ThinkingResponse:
    type: str = "thinking"
    node: str = ""
    message: str = ""
    progress: float = 0.0

    def to_dict(self):
        return {
            "type": self.type,
            "node": self.node,
            "message": self.message,
            "progress": self.progress
        }


@dataclass
class ContentResponse:
    type: str = "content"
    node: str = ""
    data: Any = None
    format: str = "json"  # json, html, text

    def to_dict(self):
        return {
            "type": self.type,
            "node": self.node,
            "data": self.data,
            "format": self.format
        }


# Helper Functions for Response Formatting
def create_thinking_response(node_name: str, message: str, progress: float = 0.0) -> Dict[str, Any]:
    """
    Helper function to create standardized thinking responses

    Args:
        node_name: Name of the node generating the response
        message: Status message describing current processing
        progress: Progress value between 0.0 and 1.0

    Returns:
        Dictionary representation of thinking response
    """
    return ThinkingResponse(
        node=node_name,
        message=message,
        progress=progress
    ).to_dict()


def create_content_response(node_name: str, data: Any, format_type: str = "json") -> Dict[str, Any]:
    """
    Helper function to create standardized content responses

    Args:
        node_name: Name of the node generating the response
        data: The actual content/results to return
        format_type: Type of content format ("json", "html", "text")

    Returns:
        Dictionary representation of content response
    """
    return ContentResponse(
        node=node_name,
        data=data,
        format=format_type
    ).to_dict()


def create_progress_thinking_response(node_name: str, message: str, current_step: int, total_steps: int) -> Dict[
    str, Any]:
    """
    Helper function to create thinking responses with calculated progress

    Args:
        node_name: Name of the node generating the response
        message: Status message describing current processing
        current_step: Current step number (1-based)
        total_steps: Total number of steps

    Returns:
        Dictionary representation of thinking response with calculated progress
    """
    progress = min(current_step / total_steps, 1.0) if total_steps > 0 else 0.0
    return create_thinking_response(node_name, message, progress)


def create_error_response(node_name: str, error_message: str) -> Dict[str, Any]:
    """
    Helper function to create standardized error responses

    Args:
        node_name: Name of the node where error occurred
        error_message: Description of the error

    Returns:
        Dictionary representation of error response
    """
    return {
        "type": "error",
        "node": node_name,
        "message": error_message,
        "timestamp": time.time()
    }


# Graph State
class GraphState(TypedDict):
    user_input: str
    decision: str
    processing_type: str
    results: Any
    metadata: Dict[str, Any]


# Node Functions
def decision_node(state: GraphState) -> Generator[Dict[str, Any], None, None]:
    """Node that makes a decision based on customer input"""
    yield ThinkingResponse(
        node="decision_node",
        message="Analyzing user input to determine processing path...",
        progress=0.1
    ).to_dict()

    time.sleep(1)  # Simulate processing

    user_input = state.get("user_input", "").lower()

    if "data" in user_input or "analysis" in user_input:
        decision = "data_processing"
        state["decision"] = decision
        state["processing_type"] = "data_analysis"
    elif "report" in user_input or "summary" in user_input:
        decision = "report_generation"
        state["decision"] = decision
        state["processing_type"] = "report_creation"
    else:
        decision = "general_processing"
        state["decision"] = decision
        state["processing_type"] = "general_task"

    yield ThinkingResponse(
        node="decision_node",
        message=f"Decision made: routing to {decision}",
        progress=1.0
    ).to_dict()


def data_processing_node(state: GraphState) -> Generator[Dict[str, Any], None, None]:
    """Long-running data processing simulation"""
    yield ThinkingResponse(
        node="data_processing_node",
        message="Initializing data processing pipeline...",
        progress=0.0
    ).to_dict()

    time.sleep(2)

    yield ThinkingResponse(
        node="data_processing_node",
        message="Loading and validating data sources...",
        progress=0.3
    ).to_dict()

    time.sleep(1.5)

    yield ThinkingResponse(
        node="data_processing_node",
        message="Performing statistical analysis...",
        progress=0.7
    ).to_dict()

    time.sleep(1.5)

    # Generate mock results
    results = {
        "total_records": 15847,
        "categories": ["A", "B", "C", "D"],
        "summary_stats": {
            "mean": 42.7,
            "median": 38.5,
            "std_dev": 12.3
        },
        "insights": [
            "Category A shows highest performance",
            "Trend indicates 15% growth over period",
            "Outliers detected in Q3 data"
        ]
    }

    state["results"] = results

    yield ContentResponse(
        node="data_processing_node",
        data=results,
        format="json"
    ).to_dict()


def report_generation_node(state: GraphState) -> Generator[Dict[str, Any], None, None]:
    """Long-running report generation simulation"""
    yield ThinkingResponse(
        node="report_generation_node",
        message="Setting up report template...",
        progress=0.0
    ).to_dict()

    time.sleep(1.5)

    yield ThinkingResponse(
        node="report_generation_node",
        message="Gathering data sources...",
        progress=0.25
    ).to_dict()

    time.sleep(1.5)

    yield ThinkingResponse(
        node="report_generation_node",
        message="Generating visualizations...",
        progress=0.6
    ).to_dict()

    time.sleep(1)

    yield ThinkingResponse(
        node="report_generation_node",
        message="Compiling final report...",
        progress=0.9
    ).to_dict()

    time.sleep(1)

    # Generate HTML report
    html_report = """
    <div class="report">
        <h1>Executive Summary Report</h1>
        <div class="section">
            <h2>Key Findings</h2>
            <ul>
                <li>Revenue increased by 23% year-over-year</li>
                <li>Customer satisfaction scores improved to 4.2/5.0</li>
                <li>Market share expanded in key demographics</li>
            </ul>
        </div>
        <div class="section">
            <h2>Recommendations</h2>
            <p>Focus on digital transformation initiatives and customer experience optimization.</p>
        </div>
        <div class="metrics">
            <div class="metric">
                <span class="label">Total Revenue:</span>
                <span class="value">$2.4M</span>
            </div>
            <div class="metric">
                <span class="label">Growth Rate:</span>
                <span class="value">23%</span>
            </div>
        </div>
    </div>
    """

    state["results"] = html_report

    yield ContentResponse(
        node="report_generation_node",
        data=html_report,
        format="html"
    ).to_dict()


def general_processing_node(state: GraphState) -> Generator[Dict[str, Any], None, None]:
    """General processing with text output"""
    yield ThinkingResponse(
        node="general_processing_node",
        message="Processing general request...",
        progress=0.0
    ).to_dict()

    time.sleep(2)

    yield ThinkingResponse(
        node="general_processing_node",
        message="Analyzing requirements...",
        progress=0.4
    ).to_dict()

    time.sleep(1.5)

    yield ThinkingResponse(
        node="general_processing_node",
        message="Generating response...",
        progress=0.8
    ).to_dict()

    time.sleep(1.5)

    # Generate text summary
    summary = f"""
    Processing Summary for: "{state.get('user_input', 'Unknown request')}"

    Analysis Complete:
    - Request type: General processing
    - Processing time: ~5 seconds
    - Status: Completed successfully

    Results:
    Your request has been processed through our general pipeline. The system
    has analyzed your input and determined this requires standard processing
    protocols. All checks have passed and the task has been completed.

    Next steps:
    - Review the processing results
    - Contact support if additional assistance is needed
    - Submit follow-up requests as necessary
    """

    state["results"] = summary.strip()

    yield ContentResponse(
        node="general_processing_node",
        data=summary.strip(),
        format="text"
    ).to_dict()


# Decision function for conditional routing
def route_decision(state: GraphState) -> str:
    decision = state.get("decision", "general_processing")
    return decision


# Build the graph
def create_graph() -> CompiledGraph:
    graph = StateGraph()

    # Add nodes
    graph.add_node("decision", decision_node)
    graph.add_node("data_processing", data_processing_node)
    graph.add_node("report_generation", report_generation_node)
    graph.add_node("general_processing", general_processing_node)

    # Set entry point
    graph.set_entry_point("decision")

    # Add conditional routing from decision node
    graph.add_conditional_edges(
        "decision",
        route_decision,
        {
            "data_processing": "data_processing",
            "report_generation": "report_generation",
            "general_processing": "general_processing"
        }
    )

    # All processing nodes end the graph
    graph.add_edge("data_processing", "END")
    graph.add_edge("report_generation", "END")
    graph.add_edge("general_processing", "END")

    return graph.compile()


# Flask Application
app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=4)


def run_graph_stream(user_input: str) -> Generator[str, None, None]:
    """Generator function that runs the graph and yields JSON responses"""
    try:
        # Initialize state
        initial_state: GraphState = {
            "user_input": user_input,
            "decision": "",
            "processing_type": "",
            "results": None,
            "metadata": {"start_time": time.time()}
        }

        # Create and run graph
        graph = create_graph()

        for result in graph.stream(initial_state):
            yield f"data: {json.dumps(result)}\n\n"

        # Send completion signal
        completion = {
            "type": "complete",
            "message": "Processing finished",
            "total_time": time.time() - initial_state["metadata"]["start_time"]
        }
        yield f"data: {json.dumps(completion)}\n\n"

    except Exception as e:
        error_response = {
            "type": "error",
            "message": f"An error occurred: {str(e)}"
        }
        yield f"data: {json.dumps(error_response)}\n\n"


@app.route('/process', methods=['GET'])
def process_request():
    """
    GET endpoint that accepts user input and returns a streamed response

    Query Parameters:
    - input: The user input text to process

    Returns:
    - Server-Sent Events stream with JSON data
    """
    user_input = request.args.get('input', '')

    if not user_input:
        return jsonify({"error": "Missing 'input' parameter"}), 400

    def generate():
        yield "data: " + json.dumps({
            "type": "start",
            "message": "Starting processing...",
            "input": user_input
        }) + "\n\n"

        # Run the graph in the current thread
        for chunk in run_graph_stream(user_input):
            yield chunk

    return Response(
        generate(),
        mimetype='text/plain',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'text/plain; charset=utf-8'
        }
    )


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": time.time()})


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with usage information"""
    return jsonify({
        "message": "LangGraph Flask Streaming API",
        "endpoints": {
            "/process": "GET - Process user input with streaming response (param: input)",
            "/health": "GET - Health check",
            "/": "GET - This help message"
        },
        "example": "/process?input=analyze the sales data",
        "response_types": {
            "thinking": "Updates from nodes during processing",
            "content": "Final results from end-state nodes",
            "complete": "Processing finished signal",
            "error": "Error messages"
        }
    })


if __name__ == '__main__':
    print("Starting LangGraph Flask Streaming Application...")
    print("Available endpoints:")
    print("  GET /process?input=<your_input>  - Process input with streaming")
    print("  GET /health                      - Health check")
    print("  GET /                           - API documentation")
    print("\nExample requests:")
    print("  curl 'http://localhost:5000/process?input=analyze%20the%20data'")
    print("  curl 'http://localhost:5000/process?input=generate%20a%20report'")
    print("  curl 'http://localhost:5000/process?input=help%20me%20with%20something'")

    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)