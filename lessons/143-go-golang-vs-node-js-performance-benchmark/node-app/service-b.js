import express from "express";
import { MongoClient } from "mongodb";
import config from "./config.json" assert { type: 'json' };

const app = express();
const client = new MongoClient(config.mongodbUri);

const getTime = (req, res) => {
    const d = new Date();
    res.send({ lastModified: d.toISOString() });
}

const saveModifiedDate = (req, res) => {
    let date = req.body.lastModified;

    save("lesson143", "images", date).catch(console.dir);
    res.send({ lastModified: date });
}

const save = async (db, collection, date) => {
    try {
        const database = client.db(db);
        const imageRecord = database.collection(collection);

        await imageRecord.insertOne({ lastModified: date });
    } catch (e) {
        console.log(e);
    }
}

app.use(express.json());
app.get('/api/time', getTime);
app.post('/api/images/:name', saveModifiedDate);

app.listen(config.serviceBPort, () => {
    console.log(`App listening on port ${config.serviceBPort}`);
});
