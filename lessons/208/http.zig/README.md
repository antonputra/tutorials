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


HTTP.zig in ReleaseFast mode
```
Running 30s test @ http://localhost:8086/api/devices
  4 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   492.28us  185.23us   6.05ms   83.81%
    Req/Sec    50.01k    11.59k   60.59k    79.05%
  5985889 requests in 30.10s, 707.86MB read
Requests/sec: 198855.02
Transfer/sec:     23.52MB
```

----

Running both with Debug compiles, similar story

```
Actix compiled in Debug mode

  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.50ms  230.25us   5.05ms   86.76%
    Req/Sec    16.73k     2.05k   67.69k    83.85%
  1999217 requests in 30.10s, 310.78MB read
Requests/sec:  66409.49
Transfer/sec:     10.32MB
```

```
Zig compiled in Debug mode

  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     0.88ms  281.05us  20.30ms   91.38%
    Req/Sec    28.58k     2.83k   59.14k    87.60%
  3418569 requests in 30.10s, 404.26MB read
Requests/sec: 113569.44
Transfer/sec:     13.43MB

```

TL;DR - much of a muchness for runtime performance ! There really isnt anything between them

Actix generally has better latency, and less scatter (std deviation)

Zig has a better peak throughput, and uses 1 third the memory (at least with these config tweaks)

-----

The main difference (to me) is that the Actix build is pulling in a huge number of dependencies :( 

The zig code is only pulling in 1 dependency
