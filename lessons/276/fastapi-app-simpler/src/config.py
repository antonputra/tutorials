import yaml


class Config:
    def __init__(self, file_path):
        self.app_port = int()
        self.db = DBConfig()

        self._load_config(file_path)

    def _load_config(self, file_path):
        try:
            with open(file_path, "r") as file:
                cfg = yaml.safe_load(file)

                self.app_port = cfg["appPort"]
                self.db.load(cfg["db"])
        except FileNotFoundError:
            print(f"Error: {file_path} not found.")
            raise
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            raise


class DBConfig:
    def __init__(self):
        self.user = str()
        self.password = str()
        self.host = str()
        self.database = str()
        self.max_connections = int()

    def load(self, cfg):
        self.user = cfg["user"]
        self.password = cfg["password"]
        self.host = cfg["host"]
        self.database = cfg["database"]
        self.max_connections = cfg["maxConnections"]
