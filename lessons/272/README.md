# Redis vs Valkey: Performance & Comparison

You can find tutorial [here](https://youtu.be/wWTjxLcMVsg).

```bash
# ec2: c8g.4xlarg
/usr/local/bin/redis-server --io-threads 9 --save --protected-mode no
/usr/local/bin/valkey-server --io-threads 9 --save --protected-mode no
```
