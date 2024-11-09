import histogram from "./metrics.js";
import save from "./devices.js";
import { randomUUID } from "crypto";
import { register } from "prom-client";
import config from "./config.js";

import uWS from "uWebSockets.js";

const app = uWS.App();

app.get("/metrics", (res) => {
  res.writeHeader("Content-Type", register.contentType);
  register.metrics().then((data) => res.end(data));
});

app.get("/healthz", (res) => {
  res.writeHeader("Content-Type", "text/plain").end("OK");
});

app.get("/api/devices", (res) => {
  const devices = [
    {
      id: 1,
      uuid: "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
      mac: "5F-33-CC-1F-43-82",
      firmware: "2.1.6",
      created_at: "2024-05-28T15:21:51.137Z",
      updated_at: "2024-05-28T15:21:51.137Z",
    },
    {
      id: 2,
      uuid: "d2293412-36eb-46e7-9231-af7e9249fffe",
      mac: "E7-34-96-33-0C-4C",
      firmware: "1.0.3",
      created_at: "2024-01-28T15:20:51.137Z",
      updated_at: "2024-01-28T15:20:51.137Z",
    },
    {
      id: 3,
      uuid: "eee58ca8-ca51-47a5-ab48-163fd0e44b77",
      mac: "68-93-9B-B5-33-B9",
      firmware: "4.3.1",
      created_at: "2024-08-28T15:18:21.137Z",
      updated_at: "2024-08-28T15:18:21.137Z",
    },
  ];

  res
    .writeHeader("Content-Type", "application/json")
    .end(JSON.stringify(devices));
});

app.post("/api/devices", (res) => {
  readJson(res, (device) => {
    const datetime = new Date();

    device.uuid = randomUUID();
    device.created_at = datetime;
    device.updated_at = datetime;

    const end = histogram.startTimer();
    save(device)
      .then((record) => {
        end({ op: "db" });

        device.id = record[0].id;

        res.cork(() => {
          res
            .writeStatus("201")
            .writeHeader("Content-Type", "application/json")
            .end(JSON.stringify(device));
        });
      })
      .catch((error) => {
        console.error(error);

        res.cork(() => {
          res
            .writeStatus("400")
            .writeHeader("Content-Type", "application/json")
            .end(JSON.stringify({ message: error.message }));
        });
      });
  });
});

app.any("/*", (res) => {
  res
    .writeStatus("404")
    .writeHeader("Content-Type", "text/plain")
    .end("Not Found");
});

app.listen(config.appPort, (token) => {
  if (token) {
    console.log(`Node is listening on http://0.0.0.0:${config.appPort} ...`);
  }
});

// Source: https://github.com/uNetworking/uWebSockets.js/blob/master/examples/JsonPost.js
/* Helper function for reading a posted JSON body */
function readJson(res, cb, err) {
  let buffer;
  /* Register data cb */
  res.onData((ab, isLast) => {
    let chunk = Buffer.from(ab);
    if (isLast) {
      let json;
      if (buffer) {
        try {
          json = JSON.parse(Buffer.concat([buffer, chunk]));
        } catch (e) {
          /* res.close calls onAborted */
          res.close();
          return;
        }
        cb(json);
      } else {
        try {
          json = JSON.parse(chunk);
        } catch (e) {
          /* res.close calls onAborted */
          res.close();
          return;
        }
        cb(json);
      }
    } else {
      if (buffer) {
        buffer = Buffer.concat([buffer, chunk]);
      } else {
        buffer = Buffer.concat([chunk]);
      }
    }
  });

  /* Register error cb */
  res.onAborted(err);
}
