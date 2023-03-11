import http from 'k6/http';
import { sleep, group, check } from 'k6';

export const options = {
    stages: [
        { target: 30, duration: '10m' },
        { target: 5, duration: '10m' },
        { target: 10, duration: '10m' },
        { target: 50, duration: '10m' },
    ]
};

const url = 'http://54.221.99.119/api/devices'

export default () => {

    group('Send GET requests', () => {
        const res = http.get(url);
        const checkRes = check(res, {
            'status is 200': (r) => r.status === 200,
        });
    });

    group('Send GET requests 2', () => {
        const res = http.get(url);
        const checkRes = check(res, {
            'status is 200': (r) => r.status === 200,
        });
    });

    group('Send GET requests 3', () => {
        const res = http.get(url);
        const checkRes = check(res, {
            'status is 200': (r) => r.status === 200,
        });
    });

    group('Send POST requests', () => {
        const res = http.post(url);
        const checkRes = check(res, {
            'status is 201': (r) => r.status === 201,
        });
    });

    group('Send wrong page requests', () => {
        const res = http.put(url);
        const checkRes = check(res, {
            'status is 405': (r) => r.status === 405,
        });
    });

    sleep(1);
};