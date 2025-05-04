import http from 'k6/http';
import { sleep, group, check } from 'k6';

export const options = {
    stages: [
        { target: 3, duration: '5m' },
        { target: 1, duration: '5m' },
        { target: 3, duration: '5m' },
        { target: 1, duration: '5m' },
        { target: 3, duration: '5m' },
        { target: 1, duration: '5m' },
        { target: 3, duration: '5m' },
        { target: 1, duration: '5m' },
        { target: 3, duration: '5m' },
        { target: 1, duration: '5m' },
        { target: 3, duration: '5m' },
        { target: 1, duration: '5m' },
    ]
};

const url = 'http://localhost:8181/api/devices'

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

    // group('Send wrong page requests', () => {
    //     const res = http.put(url);
    //     const checkRes = check(res, {
    //         'status is 405': (r) => r.status === 405,
    //     });
    // });

    sleep(1);
};
