import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';

const client = new grpc.Client();
client.load(['.'], 'event.proto');

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

// const host = '[::1]:50050'
const host = 'grpc.antonputra.pvt:443'

export default () => {
    client.connect(host, {
        plaintext: false
        // plaintext: true
    });

    const data = { id: 16753716253 };
    const response = client.invoke('event.Manager/GetEvent', data);

    check(response, {
        'status is OK': (r) => r && r.status === grpc.StatusOK,
    });

    client.close();
    sleep(1);
};