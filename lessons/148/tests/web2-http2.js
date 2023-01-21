const client = require('prom-client');
const { chromium } = require('playwright');

const Registry = client.Registry;
const register = new Registry();
const gateway = new client.Pushgateway('http://127.0.0.1:9091', [], register);

const prefix = 'nginx';
const test = 'web2';
const protocol = 'http2';

const duration = new client.Gauge({
    name: `${prefix}_duration_ms`,
    help: `${prefix} duration`,
    labelNames: ['test'],
    registers: [register],
});
register.registerMetric(duration);

(async () => {
    for (let i = 0; i < 1000; i++) {
        const browser = await chromium.launch()
        const page = await browser.newPage()
        await page.goto(`https://${protocol}.antonputra.com/${test}/`)

        const navigationTimingJson = await page.evaluate(() =>
            JSON.stringify(performance.getEntriesByType('navigation'))
        )
        const navigationTiming = JSON.parse(navigationTimingJson);

        duration.labels({ test: test }).set(navigationTiming[0].duration);

        gateway
            .push({ jobName: protocol })
            .catch(err => {
                console.log(`Error: ${err}`);
            });

        await browser.close()
        await sleep(2000)
    }
})()

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}