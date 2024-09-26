import summary from "./metrics.js";
import save from "./devices.js";
import { randomUUID } from "node:crypto";
import { register } from "prom-client";
import config from "./config.js";

import fastify from "fastify";
import { serverFactory } from "@geut/fastify-uws";

const app = fastify({
  serverFactory,
  keepAliveTimeout: 60000,
});

app.get("/metrics", (_req, res) => {
  res.header("content-type", register.contentType);

  register.metrics().then((data) => res.send(data));
});

app.get("/healthz", (_req, res) => {
  res.header("content-type", "text/plain");

  res.send("OK");
});

app.get(
  "/api/devices",
  {
    schema: {
      response: {
        200: {
          type: "object",
          properties: {
            uuid: {
              type: "string",
            },
            mac: {
              type: "string",
            },
            firmware: {
              type: "string",
            },
          },
        },
      },
    },
  },
  (req, res) => {
    const device = {
      uuid: "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
      mac: "5F-33-CC-1F-43-82",
      firmware: "2.1.6",
    };

    res.header("content-type", "application/json");

    res.status(200).send(device);
  },
);

app.post(
  "/api/devices",
  {
    schema: {
      response: {
        200: {
          type: "object",
          properties: {
            uuid: {
              type: "string",
            },
            mac: {
              type: "string",
            },
            firmware: {
              type: "string",
            },
          },
        },
        400: {
          type: "object",
          properties: {
            message: {
              type: "string",
            },
          },
        },
      },
    },
  },
  (req, res) => {
    const device = {
      uuid: randomUUID(),
      ...req.body,
    };

    const end = summary.startTimer();

    save(device)
      .then(() => {
        end({ op: "db" });

        res.status(201).header("content-type", "application/json").send(device);
      })
      .catch((error) => {
        console.error(error);

        res
          .status(400)
          .header("content-type", "application/json")
          .send({ message: error.message });
      });
  },
);

app
  .listen({ port: config.appPort, host: "0.0.0.0" })
  .then((address) => console.log("App is listening on ", address));
