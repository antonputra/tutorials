import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';

const client = new grpc.Client();
client.load(['.'], 'device.proto');

export const options = {
    stages: [
        { target: 5, duration: '5m' },
        { target: 10, duration: '0m' },
        { target: 10, duration: '5m' },
        { target: 20, duration: '5m' },
    ]
};

// const host = '[::1]:50050'
const host = 'api.go.antonputra.pvt:443'

export default () => {
    client.connect(host, {
        plaintext: false
        // plaintext: true
    });

    const data = { uuid: "b0e42fe7-31a5-4894-a441-007e5256afea" };
    const response = client.invoke('hardware.Manager/GetDevice', data);

    check(response, {
        'status is OK': (r) => r && r.status === grpc.StatusOK,
    });

    client.close();
    sleep(1);
};