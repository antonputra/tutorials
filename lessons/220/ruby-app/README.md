# README

Basic Ruby application. 25x faster than Rails on my Mac M1.

To setup database run the following commands:
```bash
bin/rake db:create
bin/rake db:migrate
```

To run the server:
```bash
bin/iodine -p 8080
```

Defaults
```bash
WORKERS_NUM=2
```

### Local benchmark

#### `rails-app`
```bash
WORKERS_NUM=2 RAILS_ENV=production rs
wrk -c 10 -t 2 -d 10 --latency http://localhost:8080/api/devices
Running 10s test @ http://localhost:8080/api/devices
  2 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.12ms  846.12us  31.20ms   94.80%
    Req/Sec     2.42k   239.12     2.66k    88.12%
  Latency Distribution
     50%    1.94ms
     75%    2.17ms
     90%    2.63ms
     99%    5.35ms
  48603 requests in 10.10s, 46.07MB read
Requests/sec:   4811.04
Transfer/sec:      4.56MB
```

#### `ruby-app`
```bash
WORKERS_NUM=2 bin/iodine -p 8080 config.ru
wrk -c 10 -t 2 -d 10 --latency http://localhost:8080/api/devices
Running 10s test @ http://localhost:8080/api/devices
  2 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   142.99us  660.05us  21.06ms   99.01%
    Req/Sec    48.48k     9.07k   60.82k    63.00%
  Latency Distribution
     50%   83.00us
     75%  112.00us
     90%  160.00us
     99%  798.00us
  965345 requests in 10.01s, 613.14MB read
Requests/sec:  96422.17
Transfer/sec:     61.24MB
```

#### `ruby-app` with docker
```bash
docker build -t ruby-app .
docker run --rm -p 8080:8080 --name ruby-app ruby-app
wrk -c 10 -t 2 -d 10 --latency http://localhost:8080/api/devices
Running 10s test @ http://localhost:8080/api/devices
  2 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   785.27us    3.26ms  62.81ms   97.92%
    Req/Sec    12.66k     3.14k   15.44k    84.50%
  Latency Distribution
     50%  351.00us
     75%  430.00us
     90%  614.00us
     99%   12.92ms
  251840 requests in 10.00s, 159.96MB read
Requests/sec:  25176.72
Transfer/sec:     15.99MB
```
