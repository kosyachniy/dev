const express = require('express')
const cors = require('cors')
const fs = require("fs");

const app = express()
app.use(cors())
app.use(express.json())

app.get('/', function (req, res) {
    console.log(req)
    fs.createReadStream('index.html').pipe(res)
})

app.post('/', function (req, res) {
    console.log(req.body)
    res.json({data: req.body})
})

app.listen(3000)
