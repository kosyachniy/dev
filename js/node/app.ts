import express, { Request, Response, Application} from 'express'
const cors = require('cors')
// const fs = require('fs')

const app: Application = express()

app.use(cors())
app.use(express.json())
app.use(express.static(__dirname + '/public'))
app.use((req: Request, res: Response, next) : void => {
    console.log('Middleware', req.url, req.headers, req.body)
    next()
})

const userRouter = express.Router()
userRouter.use('/:token', (req: Request, res: Response) : void => {
    res.send(`User ${req.params.token}`)
})
app.use('/users', userRouter)

// app.get('/', (req:Request, res:Response):void => {
//     // fs.createReadStream('index.html').pipe(res)
//     // fs.readFile('index.html', 'utf8', (err, data) => {
//     //     res.send(data)
//     // })
//     res.sendFile(__dirname + '/index.html')
// })

const generate = (length: number = 32) : string => {
    let symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'.split('');
    let token_raw = [];
    for (let i=0; i<length; i++) {
        let j: number = +(Math.random() * (symbols.length-1)).toFixed(0);
        token_raw[i] = symbols[j];
    }
    return token_raw.join('');
}

app.post('/auth', (req: Request, res: Response) => {
    res.json({token: generate()})
})

app.listen(3000)
