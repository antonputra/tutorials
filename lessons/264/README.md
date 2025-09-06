# ZeroMQ vs Aeron: Best for Market Data? Performance (Latency & Throughput)

You can find tutorial [here](https://youtu.be/wP1wz6MhxcI).

## Commands

```bash
/usr/local/bin/aeronmd \\
-Daeron.threading.mode=DEDICATED \\
-Daeron.conductor.buffer.size=16m \\
-Daeron.driver.event.log=disabled \\
-Daeron.driver.idle.strategy=busy_spin \\
-Daeron.print.configuration=true

## 1st Test
CHANNEL="aeron:udp?endpoint=10.0.89.94:40123" SLEEP_INTERVAL_US="2000" STAGE_INTERVAL_US="2000000" DECREMENT_INTERVAL_US="1" /usr/local/bin/aeron-publisher
CHANNEL="aeron:udp?endpoint=10.0.89.94:40123" /usr/local/bin/aeron-subscriber

CHANNEL="tcp://*:5555" SLEEP_INTERVAL_US="2000" STAGE_INTERVAL_US="2000000" DECREMENT_INTERVAL_US="1" /usr/local/bin/zeromq-publisher
CHANNEL="tcp://10.0.65.17:5555" /usr/local/bin/zeromq-subscriber

# 2nd Test
CHANNEL="aeron:ipc" SLEEP_INTERVAL_US="2000" STAGE_INTERVAL_US="2000000" DECREMENT_INTERVAL_US="1" /usr/local/bin/aeron-publisher
CHANNEL="aeron:ipc" /usr/local/bin/aeron-subscriber

CHANNEL="ipc:///tmp/zmq_bbo" SLEEP_INTERVAL_US="2000" STAGE_INTERVAL_US="2000000" DECREMENT_INTERVAL_US="1" /usr/local/bin/zeromq-publisher
CHANNEL="ipc:///tmp/zmq_bbo" /usr/local/bin/zeromq-subscriber
```
