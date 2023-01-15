import http from 'k6/http';
import { sleep, group, check } from 'k6';

export const options = {
    scenarios: {
        test: {
            executor: 'ramping-vus',
            startVUs: 1,
            stages: [
                { target: 1000, duration: '5m' },
                { target: 2000, duration: '0' },
                { target: 2000, duration: '5m' },
                { target: 10000, duration: '5m' },
            ],
        },
    },
};

const url = "http://api.nginx.antonputra.pvt/api-nginx/devices"

export default () => {

    group('Send GET requests', () => {
        const res = http.get(url);
        const checkRes = check(res, {
            'status is 200': (r) => r.status === 200,
        });
    });

    sleep(1);
};
