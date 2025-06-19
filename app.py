from flask import Flask, Response, request, stream_with_context
import json
import uuid
from src.agents.graph_builder import my_graph
from src.util.mermaid import create_mermaid_diagram_files

print('creating flask app')
app = Flask(__name__)
print('created flask app')
create_mermaid_diagram_files()
print('updated mermaid diagram')

@app.route('/stream-chat', methods=['POST'])
def stream_chat():
    """
    Streaming HTTP REST endpoint to invoke `my_graph.stream()` and stream data back.
    Expects a JSON payload with 'messages'.
    """
    # Parse incoming JSON payload
    data = request.get_json()
    if not data or 'messages' not in data:
        return {"error": "Invalid input. 'messages' field is required."}, 400

    # Extract messages from client request
    messages = data.get('messages')
    if not isinstance(messages, list):
        return {"error": "'messages' must be an array."}, 400

    # Generate session ID for this conversation
    session_id = uuid.uuid4()
    config = {"configurable": {"session_id": session_id}}

    def generate_stream():
        """
        Generator yielding streaming chunks from `my_graph.stream()`.
        """
        print('generate stream')
        inputs = {"messages": messages, "message_type": None}
        try:
            print('Yield each chunk in JSON format:')
            for chunk in my_graph.stream(inputs, config, stream_mode="messages"):
                result = json.dumps({"content": chunk[0].content}) + '\n'
                print(chunk[0].content, end="", flush=True)
                yield result
        except Exception as exc:
            yield json.dumps({"error": str(exc)}) + '\n'

    print('Return a streaming response')
    return Response(
        stream_with_context(generate_stream()),
        content_type='text/event-stream'
        # content_type='application/json'
    )


if __name__ == "__main__":
    print('Start Flask server')
    app.run(host="0.0.0.0", port=5001, debug=True)
