import time
import uuid
from datetime import datetime
from opentelemetry.trace import set_span_in_context


class Image:
    """Image represents the image uploaded by the user."""

    def __init__(self):
        """Create a default constructor for the Image."""

        self.uuid = self._generate_uuid()
        self.last_modified = self._get_time()

    def _generate_uuid(self):
        """Generate random UUID."""

        return str(uuid.uuid4())

    def _get_time(self):
        """Return current timestamp."""

        return datetime.now()


def download(s3, bucket, key, span, tracer, request_duration):
    """Downloads S3 image and returns last modified date."""

    # Get current time to record request duration.
    start = time.time()

    # Get current context to create child span id.
    context = set_span_in_context(span)

    # Create child span id for the S3 get request.
    with tracer.start_as_current_span("S3 GET", context) as span:

        # Download file from the S3 object store.
        object = s3.get_object(Bucket=bucket, Key=key)

        # Read all the image bytes returned by AWS.
        object['Body'].read()

        # Get current time to record request duration.
        end = time.time() - start
        request_duration.labels('s3').observe(end)

        return object['LastModified'], span


def save(image, table, pool, span, tracer, request_duration):
    """Inserts a newly generated image into the Postgres database."""

    # Get current time to record request duration.
    start = time.time()

    # Get current context to create child span id.
    context = set_span_in_context(span)

    # Create child span id for the DB Insert.
    with tracer.start_as_current_span("SQL INSERT", context) as span:

        # Connect to an existing database
        with pool.connection() as conn:

            # Open a cursor to perform database operations
            with conn.cursor() as cur:

                # Prepare the database query.
                query = f'INSERT INTO {table} (image_uuid, last_modified) VALUES (%s, %s)'

                # Send the query to PostgreSQL.
                cur.execute(query, (image.uuid, image.last_modified))

                # Make the changes to the database persistent
                conn.commit()

                # Get current time to record request duration.
                end = time.time() - start
                request_duration.labels('db').observe(end)
