import axios from 'axios';
import { server } from '../sets';

function serverRequest(method, json = {}) {
    return axios.post(server.link + method + '/', json);
}

function handlerResult(that, res, handlerSuccess, handlerError) {
    if (res.error) {
        console.log('error: ', res)
        handlerError(that, res);
    } else {
        console.log('success: ', res)
        handlerSuccess(that, res);
    }
}

export default function api(that, method, params = {}, handlerSuccess = () => {},
    handlerError = () => {}) {
    serverRequest(method, params).then((res) => handlerResult(that, res.data, handlerSuccess, handlerError));
}
