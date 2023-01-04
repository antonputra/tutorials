import http from 'k6/http';
import { sleep, group, check } from 'k6';

export const options = {
    stages: [
        { target: 30, duration: '5m' },
        { target: 1, duration: '5m' },
        { target: 10, duration: '5m' },
        { target: 50, duration: '5m' },
        { target: 50, duration: '5m' },
        { target: 20, duration: '5m' },
    ]
};

const nodeURL = "http://node-service-a.devopsbyexample.com/api/images/thumbnail.png"

export default () => {

    group('Send GET requests to Nodejs', () => {
        const res = http.get(nodeURL);
        const checkRes = check(res, {
            'status is 200': (r) => r.status === 200,
        });
    });

    sleep(1);
};
