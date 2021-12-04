import axios from 'axios'

import getToken from './token'


import { server } from '../sets'


function serverRequest(json={}) {
    console.log(server, json)
    return axios.post(server, json)
}

function handlerResult(res, handlerSuccess, handlerError) {
    if (res['error']) {
        console.log(res)
        handlerError(res)
    } else {
        console.log(res)
        handlerSuccess(res['result'])
    }
}

export default function api(
    method,
    params={},
    handlerSuccess=()=>{},
    handlerError=()=>{},
) {
    let json = {
        'method': method,
        'params': params,
    }

    json['network'] = 'web'
    json['locale'] = localStorage.getItem('locale')
    json['token'] = getToken()

    serverRequest(json).then(
        (res) => handlerResult(res.data, handlerSuccess, handlerError)
    )
}

// Socket.IO
