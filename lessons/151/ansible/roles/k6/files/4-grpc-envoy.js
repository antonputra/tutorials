import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';

const client = new grpc.Client();
client.load(['.'], 'device.proto');

export const options = {
    scenarios: {
        test: {
            executor: 'ramping-vus',
            startVUs: 1,
            stages: [
                { target: 1000, duration: '15m' },
            ],
        },
    },
};

// const host = 'localhost:8082'
const host = 'api.envoy.antonputra.pvt:8443'

export default () => {
    client.connect(host, {
        plaintext: false
        // plaintext: true
    });

    const data = { uuid: "b0e42fe7-31a5-4894-a441-007e5256afea" };
    const response = client.invoke('device.Manager/GetEnvoyDevice', data);

    check(response, {
        'status is OK': (r) => r && r.status === grpc.StatusOK,
    });

    client.close();
    sleep(1);
};