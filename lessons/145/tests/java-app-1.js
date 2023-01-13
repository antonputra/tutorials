import http from 'k6/http';
import { sleep, group, check } from 'k6';

export const options = {
    scenarios: {
        test: {
            executor: 'ramping-vus',
            startVUs: 1,
            stages: [
                { target: 100, duration: '5m' },
                { target: 500, duration: '0' },
                { target: 500, duration: '5m' },
                { target: 3000, duration: '5m' },
            ],
        },
    },
};

const url = "http://java.antonputra.pvt/api/devices"

export default () => {

    group('Send GET requests', () => {
        const res = http.get(url);
        const checkRes = check(res, {
            'status is 200': (r) => r.status === 200,
        });
    });

    sleep(1);
};
