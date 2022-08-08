const express = require('express')
const cors = require('cors')
const fs = require('fs')

const app = express()

app.use(cors())
app.use(express.json())
app.use(express.static(__dirname + '/public'))
app.use((req, res, next) => {
    console.log('Middleware', req.url, req.headers)
    next()
})

app.get('/', (req, res) => {
    // fs.createReadStream('index.html').pipe(res)
    // fs.readFile('index.html', 'utf8', (err, data) => {
    //     res.send(data)
    // })
    // res.sendFile(__dirname + '/index.html')
})

app.post('/', (req, res) => {
    res.json({data: req.body})
})

app.listen(3000)
