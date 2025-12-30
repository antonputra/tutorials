export interface Device {
  uuid: string;
  mac: string;
  firmware: string;
}

export interface User {
  id?: number;
  name: string;
  address: string;
  phone: string;
  createdAt?: Date;
  updatedAt?: Date;
}

interface DbConfig {
  user: string;
  password: string;
  host: string;
  database: string;
  maxConnections: number;
}

export interface Config {
  db: DbConfig;
  appPort: number;
}
