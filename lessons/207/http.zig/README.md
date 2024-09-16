# Pure Zig port, using http.zig

Note that there are some very app specific tweaks in the server config here, to tailor this server to the intended environment.

This doesnt do much for performance, but its mainly to get the memory usage down

## Comparison with Rust

On a Mac M2, im seeing these figures on local

testing with 

- `wrk -c 100 -d 30 -t 4 http://localhost:8080/healthz`

- `wrk -c 100 -d 30 -t 4 http://localhost:8080/api/devices`

There is really no difference between the healthz endpoint and the api/devices endpoint that needs to JSONify a struct ... so really all the time is being spent doing IO


-----

Rust in --release mode

```
2.5 MB Binary
6 MB Memory
4 Threads

Running 30s test @ http://localhost:8086/api/devices
  4 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   440.79us  167.31us   4.09ms   83.65%
    Req/Sec    46.01k     2.53k   51.07k    79.40%
  5511737 requests in 30.10s, 856.79MB read
Requests/sec: 183100.15
Transfer/sec:     28.46MB
```

HTTP.zig in ReleaseSmall mode

```
141kb Binary
2 MB Memory
4 Threads

Running 30s test @ http://localhost:8086/api/devices
  4 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   507.73us  184.11us   4.19ms   85.25%
    Req/Sec    48.57k    10.33k   57.82k    80.48%
  5819106 requests in 30.10s, 688.14MB read
Requests/sec: 193313.51
Transfer/sec:     22.86MB
```

TL;DR - much of a muchness !

There really isnt anything between them

Actix generally has better latency, and less scatter (std deviation)

Zig has a better peak throughput

We are ONLY really measuring IO behaviour here though.

I suspect things would stay about the same across the board as you add more CPU intensive endpoints
