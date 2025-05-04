import http from 'k6/http';
import { sleep, group, check } from 'k6';

export const options = {
    stages: [
        { target: 1000, duration: '5m' },
    ]
};

const traefikURL = "https://api.traefik.antonputra.pvt/api/devices"

export default () => {

    group('Send GET requests', () => {
        const res = http.get(traefikURL);
        const checkRes = check(res, {
            'status is 200': (r) => r.status === 200,
        });
    });

    sleep(1);
};