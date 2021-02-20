const faker = require('faker');

exports.handler =  async (event) => {
  const name = event.name;
  const country = faker.address.country();

  const response = {
    statusCode: 200,
    body: `Hello ${name} from ${country}`
  };
  return response;
}
