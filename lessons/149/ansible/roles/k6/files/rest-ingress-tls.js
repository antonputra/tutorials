import http from 'k6/http';
import { sleep, group, check } from 'k6';

export const options = {
    scenarios: {
        test: {
            executor: 'ramping-vus',
            startVUs: 1,
            stages: [
                { target: 50, duration: '5m' },
                { target: 100, duration: '0' },
                { target: 100, duration: '5m' },
                { target: 150, duration: '5m' },
            ],
        },
    },
};

const url = "https://rest.antonputra.pvt/api/events/123"

export default () => {

    group('Send GET requests', () => {
        const res = http.get(url);
        const checkRes = check(res, {
            'status is 200': (r) => r.status === 200,
        });
    });

    sleep(1);
};