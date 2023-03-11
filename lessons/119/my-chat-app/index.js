const express = require('express')
const bodyParser = require('body-parser')

const app = express()
const port = 8080

app.use(bodyParser.json())

app.get('/connect', async (req, res) => {
    console.log('/connect endpoint is invoked')
    res.sendStatus(200)
})

app.post('/joinroom', async (req, res) => {
    console.log('/joinroom endpoint is invoked')
    console.log('headers:', req.headers)
    console.log('query:', req.query)
    console.log('body:', req.body)

    res.sendStatus(200)
})

app.listen(port, () => {
    console.log(`App listening on port ${port}`)
})
