import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';

const client = new grpc.Client();
client.load(['.'], 'device.proto');

export const options = {
    stages: [
        { target: 1000, duration: '5m' },
    ]
};

const host = 'grpc.traefik.antonputra.pvt:443'
// const host = 'api-grpc.devopsbyexample.com:443'

export default () => {
    client.connect(host, {
        plaintext: false
        // plaintext: true
    });

    const data = { uuid: "b0e42fe7-31a5-4894-a441-007e5256afea" };
    const response = client.invoke('device.Manager/GetDevice', data);

    check(response, {
        'status is OK': (r) => r && r.status === grpc.StatusOK,
    });

    // console.log(JSON.stringify(response.message));

    client.close();
    sleep(1);
};
