const security = require('../security');
const event = require('./event.json');

test('validate slack request', () => {
    const signingSecret = "0726fa5c951306c31fbe0c329d2ce736";
    expect(security.validateSlackRequest(event, signingSecret)).toBe(true);
});
