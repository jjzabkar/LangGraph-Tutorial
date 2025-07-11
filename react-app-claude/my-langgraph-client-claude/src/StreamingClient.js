import React, { useState, useRef } from 'react';
import { Send, Loader2, CheckCircle, AlertCircle, Activity } from 'lucide-react';

const StreamingClient = () => {
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentThinking, setCurrentThinking] = useState(null);
  const [contentResult, setContentResult] = useState(null);
  const [error, setError] = useState(null);
  const [processingTime, setProcessingTime] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('idle');
  const eventSourceRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;

    // Reset state
    setIsProcessing(true);
    setCurrentThinking(null);
    setContentResult(null);
    setError(null);
    setProcessingTime(null);
    setConnectionStatus('connecting');

    try {
      const encodedInput = encodeURIComponent(input.trim());
      const url = `http://localhost:5000/process?input=${encodedInput}`;

      // Create EventSource for streaming
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;
      setConnectionStatus('connected');

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          switch (data.type) {
            case 'start':
              setConnectionStatus('processing');
              break;

            case 'thinking':
              setCurrentThinking(data);
              break;

            case 'content':
              setContentResult(data);
              setCurrentThinking(null); // Clear thinking when content arrives
              break;

            case 'complete':
              setProcessingTime(data.total_time);
              setConnectionStatus('completed');
              setIsProcessing(false);
              eventSource.close();
              break;

            case 'error':
              setError(data.message);
              setConnectionStatus('error');
              setIsProcessing(false);
              eventSource.close();
              break;

            default:
              console.log('Unknown message type:', data.type);
          }
        } catch (parseError) {
          console.error('Error parsing message:', parseError);
          setError('Failed to parse server response');
        }
      };

      eventSource.onerror = (error) => {
        console.error('EventSource error:', error);
        setError('Connection error occurred');
        setConnectionStatus('error');
        setIsProcessing(false);
        eventSource.close();
      };

    } catch (error) {
      console.error('Error starting request:', error);
      setError('Failed to start request');
      setConnectionStatus('error');
      setIsProcessing(false);
    }
  };

  const handleStop = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsProcessing(false);
    setConnectionStatus('stopped');
  };

  const getConnectionStatusIcon = () => {
    switch (connectionStatus) {
      case 'connecting':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case 'connected':
      case 'processing':
        return <Activity className="h-4 w-4 text-green-500 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'error':
      case 'stopped':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const renderContent = () => {
    if (!contentResult) return null;

    const { data, format, node } = contentResult;

    switch (format) {
      case 'html':
        return (
          <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg">
            <div className="text-sm text-gray-500 mb-2">HTML Result from {node}:</div>
            <div
              className="prose max-w-none"
              dangerouslySetInnerHTML={{ __html: data }}
            />
          </div>
        );

      case 'json':
        return (
          <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg">
            <div className="text-sm text-gray-500 mb-2">JSON Result from {node}:</div>
            <pre className="bg-gray-50 p-3 rounded text-sm overflow-auto">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        );

      case 'text':
        return (
          <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg">
            <div className="text-sm text-gray-500 mb-2">Text Result from {node}:</div>
            <div className="whitespace-pre-wrap text-gray-800">
              {data}
            </div>
          </div>
        );

      default:
        return (
          <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg">
            <div className="text-sm text-gray-500 mb-2">Result from {node}:</div>
            <div>{String(data)}</div>
          </div>
        );
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-50 min-h-screen">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">
          LangGraph Streaming Client
        </h1>

        {/* Input Form */}
        <div className="mb-6">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSubmit(e)}
              placeholder="Enter your request (e.g., 'analyze the data', 'generate a report', 'help me with something')"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isProcessing}
            />
            <button
              onClick={handleSubmit}
              disabled={isProcessing || !input.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Processing
                </>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  Send
                </>
              )}
            </button>
            {isProcessing && (
              <button
                type="button"
                onClick={handleStop}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Stop
              </button>
            )}
          </div>
        </div>

        {/* Connection Status */}
        <div className="flex items-center gap-2 mb-4">
          {getConnectionStatusIcon()}
          <span className="text-sm text-gray-600 capitalize">
            Status: {connectionStatus}
          </span>
          {processingTime && (
            <span className="text-sm text-gray-500 ml-4">
              Total time: {processingTime.toFixed(2)}s
            </span>
          )}
        </div>

        {/* Current Thinking Display */}
        {currentThinking && (
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm font-medium text-blue-800">
                Processing in {currentThinking.node}
              </div>
              <div className="text-sm text-blue-600">
                {Math.round(currentThinking.progress * 100)}%
              </div>
            </div>
            <div className="text-blue-700 mb-2">
              {currentThinking.message}
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${currentThinking.progress * 100}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <div className="text-red-800 font-medium">Error</div>
            </div>
            <div className="text-red-700 mt-1">{error}</div>
          </div>
        )}

        {/* Content Result Display */}
        {renderContent()}

        {/* Example Inputs */}
        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Example Inputs:</h3>
          <div className="grid gap-2">
            <button
              onClick={() => setInput('analyze the sales data')}
              disabled={isProcessing}
              className="text-left p-2 bg-white border border-gray-200 rounded hover:bg-gray-50 disabled:opacity-50"
            >
              <span className="text-blue-600">analyze the sales data</span>
              <span className="text-gray-500 text-sm ml-2">→ Data processing with JSON output</span>
            </button>
            <button
              onClick={() => setInput('generate a quarterly report')}
              disabled={isProcessing}
              className="text-left p-2 bg-white border border-gray-200 rounded hover:bg-gray-50 disabled:opacity-50"
            >
              <span className="text-blue-600">generate a quarterly report</span>
              <span className="text-gray-500 text-sm ml-2">→ Report generation with HTML output</span>
            </button>
            <button
              onClick={() => setInput('help me process this request')}
              disabled={isProcessing}
              className="text-left p-2 bg-white border border-gray-200 rounded hover:bg-gray-50 disabled:opacity-50"
            >
              <span className="text-blue-600">help me process this request</span>
              <span className="text-gray-500 text-sm ml-2">→ General processing with text output</span>
            </button>
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h3 className="text-sm font-medium text-yellow-800 mb-2">Instructions:</h3>
          <ul className="text-sm text-yellow-700 space-y-1">
            <li>• Make sure the Flask server is running on localhost:5000</li>
            <li>• "Thinking" responses will update in real-time with progress bars</li>
            <li>• "Content" responses will display the final results</li>
            <li>• Different keywords trigger different processing paths</li>
            <li>• The connection will remain open until processing completes</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default StreamingClient;