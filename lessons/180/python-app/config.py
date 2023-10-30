import yaml


class S3Config:
    """S3Config represents configuration for the S3."""

    # Region for the S3 bucket.
    region = str()

    # S3 bucket name to store images.
    bucket = str()

    # S3 endpoint, since we use Minio we must provide
    # a custom endpoint. It should be a DNS of Minio instance.
    endpoint = str()

    # Enable path S3 style; we must enable it to use Minio.
    path_Style = bool()

    # User to access S3 bucket.
    user = str()

    # Secret to access S3 bucket.
    secret = str()

    def load(self, config):
        """Loads S3 config from dictionary."""

        # Set class properties with values from the dictionary.
        self.region = config.get('region')
        self.bucket = config.get('bucket')
        self.endpoint = config.get('endpoint')
        self.path_style = config.get('pathStyle')
        self.user = config.get('user')
        self.secret = config.get('secret')


class DbConfig:
    """DbConfig represents configuration for the Postgres."""

    # User to connect database.
    user = str()

    # Password to connect database.
    password = str()

    # Host to connect database.
    host = str()

    # Database to store images.
    database = str()

    def load(self, config):
        """Loads database config from dictionary."""

        # Set class properties with values from the dictionary.
        self.user = config.get('user')
        self.password = config.get('password')
        self.host = config.get('host')
        self.database = config.get('database')


class Config:
    """Config represents configuration for the app."""

    # Port to run the http server.
    app_port = str()

    # OTLP Endpoint to send traces.
    otlp_endpoint = str()

    # S3 config to connect to a bucket.
    s3_config = S3Config()

    # DB config to connect to a database.
    db_config = DbConfig()

    def load(self, path):
        """Loads app config from YAML file."""

        # Read the config file from the disk.
        with open(path, 'r') as file:
            # Convert the YAML config into a Python dictionary.
            config = yaml.safe_load(file)

            # Set class properties with values from the dictionary.
            self.app_port = config.get('appPort')
            self.otlp_endpoint = config.get('otlpEndpoint')
            self.s3_config.load(config.get('s3'))
            self.db_config.load(config.get('db'))
