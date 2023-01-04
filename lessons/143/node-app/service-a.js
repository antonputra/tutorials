import express from "express";
import aws from "aws-sdk";
import config from "./config.json" assert { type: "json" };
import http from "http";

const s3 = new aws.S3({
    accessKeyId: config.user,
    secretAccessKey: config.secret,
    s3ForcePathStyle: config.pathStyle,
    endpoint: config.endpoint,
});

const app = express();

const getTime = (reqquest, response) => {
    const options = {
        host: config.serviceBHost,
        port: config.serviceBPort,
        path: '/api/time',
        method: 'GET',
    };

    const callback = (resp) => {
        let str = '';
        resp.on('data', (chunk) => { str += chunk });
        resp.on('end', () => { response.send(str) });
    }

    http.request(options, callback).end();
}

const download = (bucket, key, callback) => {
    const params = { Bucket: bucket, Key: key };

    s3.getObject(params, (err, data) => {
        if (err) console.log(err);
        callback(data.LastModified);
    });
};

const getImage = (reqquest, response) => {
    let name = reqquest.params.name

    download(config.bucket, name, (date) => {
        const data = JSON.stringify({ "lastModified": date });

        const options = {
            host: config.serviceBHost,
            port: config.serviceBPort,
            path: `/api/images/${name}`,
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        };

        const callback = (resp) => {
            let str = '';
            resp.on('data', (chunk) => { str += chunk });
            resp.on('end', () => { response.send(str) });
        }

        const req = http.request(options, callback);
        req.write(data);
        req.end();
    })
}

app.use(express.json());
app.get('/api/time', getTime);
app.get('/api/images/:name', getImage);

app.listen(config.serviceAPort, () => {
    console.log(`App listening on port ${config.serviceAPort}`);
});
