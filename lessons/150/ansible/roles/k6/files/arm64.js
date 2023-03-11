import http from 'k6/http';
import { sleep, group, check } from 'k6';

export const options = {
    scenarios: {
        test: {
            executor: 'ramping-vus',
            startVUs: 6,
            stages: [
                { target: 6, duration: '30m' }
            ],
        },
    },
};

const arm64Url = "http://api.arm64.antonputra.pvt/api/keypair"
const amd64Url = "http://api.amd64.antonputra.pvt/api/keypair"

export default () => {

    group('Send GET requests', () => {
        const res = http.get(arm64Url);
        const checkRes = check(res, {
            'status is 200': (r) => r.status === 200,
        });
    });

    group('Send GET requests', () => {
        const res = http.get(amd64Url);
        const checkRes = check(res, {
            'status is 200': (r) => r.status === 200,
        });
    });

    sleep(1);
};
