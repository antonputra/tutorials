import http from 'k6/http';
import { sleep, group, check } from 'k6';

export const options = {
    scenarios: {
        test: {
            executor: 'ramping-vus',
            startVUs: 1,
            stages: [
                { target: 20, duration: '60m' },
            ],
        },
    },
};

const jsonUrl = "https://rest.antonputra.pvt/api/test-json"
const protoUrl = "https://rest.antonputra.pvt/api/test-protobuf"

export default () => {

    group('Test JSON serialization', () => {
        const res = http.get(jsonUrl);
        const checkRes = check(res, {
            'status is 200': (r) => r.status === 200,
        });
    });

    group('Test ProtoBuf serialization', () => {
        const res = http.get(protoUrl);
        const checkRes = check(res, {
            'status is 200': (r) => r.status === 200,
        });
    });

    sleep(1);
};
