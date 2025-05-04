import { Summary } from "prom-client";

// A metric to record the duration of requests,
// such as database queries or requests to the S3 object store.
const summary = new Summary({
  name: "myapp_request_duration_seconds",
  help: "Duration of the request.",
  percentiles: [0.9, 0.99],
  labelNames: ["op"],
});

export default summary;
