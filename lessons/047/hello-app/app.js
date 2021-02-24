const faker = require('faker');

exports.hello =  async (event) => {
  const data = event.body;
  const buff = new Buffer.from(data, 'base64');
  const reqString = buff.toString('ascii');
  const reqJson = JSON.parse(reqString);

  const country = faker.address.country();

  const response = {
    statusCode: 200,
    body: `Hello ${reqJson.name} from ${country}`
  };
  return response;
}
