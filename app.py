from flask import Flask, request, Response
import os
import time
from prometheus_client import generate_latest, Counter, Histogram, Gauge
import json
import logging

# OpenTelemetry Imports
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Configure basic logging for console output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure OpenTelemetry
# Resource defines attributes for your service
resource = Resource.create({
    "service.name": "my-flask-app",
    "service.version": "1.1",
    "env": "production"
})

# Set up TracerProvider
provider = TracerProvider(resource=resource)

# Configure OTLP exporter to send traces to Google Cloud Trace
# The default endpoint for Google Cloud Trace OTLP is "trace.googleapis.com:4317"
# No API key is needed if running on GKE with appropriate IAM permissions
span_exporter = OTLPSpanExporter(endpoint="trace.googleapis.com:4317", timeout=10)
provider.add_span_processor(BatchSpanProcessor(span_exporter))
trace.set_tracer_provider(provider)

# Initialize Flask app
app = Flask(__name__)

# Instrument Flask and Requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument() # To trace outgoing requests if your app made any

# Prometheus Metrics (from Week 3)
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP Request Latency',
    ['method', 'endpoint']
)
IN_PROGRESS_REQUESTS = Gauge(
    'http_requests_in_progress',
    'Number of in-progress HTTP requests',
    ['method', 'endpoint']
)

@app.route('/')
def hello():
    start_time = time.time()
    method = request.method
    endpoint = '/'

    IN_PROGRESS_REQUESTS.labels(method=method, endpoint=endpoint).inc()

    # Get the current tracer
    tracer = trace.get_tracer(__name__)
    try:
        # Create a custom span for this operation
        with tracer.start_as_current_span("hello-endpoint-processing") as span:
            span.set_attribute("http.method", method)
            span.set_attribute("http.path", endpoint)

            message = "Hello from Flask on GKE! (Version 1.1 with Tracing)"

            # Structured logging example (from Week 3)
            log_entry = {
                "severity": "INFO",
                "message": message,
                "service_name": "my-flask-app",
                "http_method": method,
                "http_path": endpoint,
                "request_id": request.headers.get('X-Request-ID', 'N/A')
            }
            logger.info(json.dumps(log_entry))

            # Simulate some work (for the practical exercise later)
            # time.sleep(0.1) # Uncomment this later for the practical exercise

            return message
    finally:
        IN_PROGRESS_REQUESTS.labels(method=method, endpoint=endpoint).dec()
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)

# --- IMPORTANT: These lines are now unindented to the top level ---
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
