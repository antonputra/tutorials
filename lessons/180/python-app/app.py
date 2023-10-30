import boto3
from flask import Flask
from psycopg_pool import ConnectionPool
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Summary, generate_latest
from devices import devices
from config import Config
from images import download
from images import save
from images import Image

# Load app config from yaml file.
config = Config()
config.load('config.yaml')

# Start configuring OpenTelemetry.
resource = Resource(attributes={
    SERVICE_NAME: "python-app"
})
provider = TracerProvider(resource=resource)

# OpenTelemetry Protocol Exporter (OTLP) Exporter
processor = BatchSpanProcessor(OTLPSpanExporter(
    # Change default HTTPS -> HTTP.
    insecure=True,

    # Update default OTLP reciver endpoint.
    endpoint=config.otlp_endpoint)
)
provider.add_span_processor(processor)

# Sets the global default tracer provider.
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider.
tracer = trace.get_tracer("python-app")


def s3Connect(config):
    """Initializes the S3 session."""

    # Create S3 config.
    s3 = boto3.client('s3',
                      endpoint_url=config.s3_config.endpoint,
                      aws_access_key_id=config.s3_config.user,
                      aws_secret_access_key=config.s3_config.secret,
                      aws_session_token=None,
                      config=boto3.session.Config(
                          signature_version='s3v4'),
                      verify=False
                      )

    return s3


def dbConnect(config):
    """Create a connection pool to connect to Postgres."""

    # Create a connection URL for the database.
    url = f'host={config.db_config.host} dbname={config.db_config.database} user={config.db_config.user} password={config.db_config.password}'

    # Connect to the Postgres database.
    pool = ConnectionPool(url)
    pool.wait()

    return pool


# Create an AWS session for S3.
s3 = s3Connect(config)

# Create a connection pool for Postgres.
pool = dbConnect(config)

# Initialize a Flask app.
app = Flask(__name__)

# Create summary metrics to record request duration for S3 and SQL requests.
request_duration = Summary(name='request_duration_seconds',
                           namespace='myapp',
                           documentation='Duration of the request.',
                           labelnames=['op'])


@app.route("/api/devices", methods=['GET'])
def get_devices():
    """Responds with the list of all connected devices as JSON."""

    return devices, 200


@app.route('/api/images', methods=['GET'])
def get_image():
    """Downloads image from S3."""

    # Creates a trace id and root span id.
    with tracer.start_as_current_span("HTTP GET /api/images") as span:
        # Optionally, set well-known span attributes.
        span.set_attribute(SpanAttributes.HTTP_METHOD, "GET")

        # Download an image from S3 and return the span context.
        _, span = download(s3, config.s3_config.bucket,
                           'thumbnail.png', span, tracer, request_duration)

        # Create a new image with a random UUID and the current timestamp.
        image = Image()

        # Save the image metadata to the PostgreSQL database.
        save(image, 'python_image', pool, span, tracer, request_duration)

        return {"message": "saved"}, 200


@app.route("/health", methods=['GET'])
def get_health():
    """Responds with a HTTP 200 or 5xx on error."""

    return {"status": "up"}, 200


@app.route('/metrics')
def metrics():
    """Exposes Prometheus metrics."""

    return generate_latest()
