const { Counter, register } = require('prom-client');
const express = require('express');
const app = express();
const port = 8081;
const host = '0.0.0.0';

app.use(express.json());

const counter = new Counter({
    name: 'http_requests_total',
    help: 'Total number of http requests',
    labelNames: ['method'],
});

const fibonacci = (num) => {
    if (num <= 1) return 1;
    return fibonacci(num - 1) + fibonacci(num - 2);
}

app.post('/fibonacci', (req, res) => {
    const fibonacciNumber = fibonacci(req.body.number);
    counter.inc({ method: 'POST' })
    res.send(`Fibonacci number is ${fibonacciNumber}!\n`);
});

app.get('/metrics', async (req, res) => {
    res.set('Content-Type', register.contentType);
    res.end(await register.getSingleMetricAsString('http_requests_total'));
});

app.listen(port, host, () => {
    console.log(`Server listening at http://${host}:${port}`);
});
