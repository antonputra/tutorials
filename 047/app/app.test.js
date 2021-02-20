const index = require('./app')
const fs = require('fs')

test('Runs function handler', async () => {
    let eventFile = fs.readFileSync('event.json')
    let event = JSON.parse(eventFile)
    let response = await index.handler(event, null)
    expect(JSON.stringify(response)).toContain('Hello Ant from')
  }
)
