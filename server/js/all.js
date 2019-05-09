// import axios from 'axios'

// import { appId, appCode } from '../keys.js'
// import console = require('console');

// import jsonpAdapter from 'axios-jsonp'
import $ from 'jquery'

// function myCallbackFunction(e) {
// 	console.log(e)
// }

function serverRequest(link, method, data) {
	// const link = 'https://weather.api.here.com/weather/1.0/report.json?product=observation&name=Saint-Petersburg&app_id=' + appId + '&app_code=' + appCode // + `&jsoncallback=myCallbackFunction`

	// let config = {
	// 	baseURL: 'https://weather.api.here.com/weather/1.0/',
	// 	proxyHeaders: false,
	// 	credentials: false,
	// 	// headers: {'Access-Control-Allow-Origin': '*'},
	// 	// headers: {
	// 	// 	'Content-Type': 'application/x-www-form-urlencoded'
	// 	//   }
	// 	// mode: 'no-cors',
	// }

// 	// return axios({
// 	// 	method: 'get',
// 	// 	url: link,
// 	// 	headers: {
// 	// 		'Content-Type': 'text/plain;charset=utf-8',
// 	// 	},
// 	// })
// // axios.defaults.headers.common['Access-Control-Request-Headers'] = null
// // axios.defaults.headers.common['Access-Control-Request-Method'] = null
	// const la = axios.get(link, config)



	// const la = axios.get(link)
	// console.log(la)
	// return la



// return new Promise(function(resolve, reject) {
// 	const request = require("request");
// 	const data = request({
// 		'url': link,
// 		'method': "GET",
// 		// 'json': json
// 	}, function(error, response, body) {
// 		if (!error && response.statusCode === 200) {
// 			resolve(body);
// 		} else {
// 			console.log("error: " + error);
// 			// console.log("response.statusCode: " + response.statusCode);
// 			// console.log("response.statusText: " + response.statusText);
// 		}
// 	});
// });

// fetch(link).then(res => {res.text().then(data=> {console.log(data)})})



return new Promise(function(resolve, reject) {
	$.ajax({
		url: link,
		type: method,
		dataType: 'jsonp',
		jsonp: 'jsonpcallback',
		data,
		success: function (data) {
			resolve(data)
		}
	  })
})

}


// function serverRequest() {
// 	const urlRequest = 'https://weather.api.here.com/weather/1.0/report.json?product=observation&name=Saint-Petersburg&app_id=' + appId + '&app_code=' + appCode
// 	let request = new XMLHttpRequest();
// 	request.open('GET', urlRequest, true);
// 	request.send();
// 	if (request.status !== 200) {
// 	console.log(request.status + ': ' + request.statusText);
// 	} else {
// 	let response = request.responseText;
// 	response = JSON.parse(response);
// 	return response;
// 	}
// 	}
	
	// function serverAsyncResponse(urlRequest){
	// var xhr = new XMLHttpRequest();
	// xhr.open('GET', 'phones.json', true);
	// xhr.send();
	// xhr.onreadystatechange = function() {
	// if (xhr.readyState != 4) return;
	// if (xhr.status != 200) {
	// console.log(xhr.status + ': ' + xhr.statusText);
	// } else {
	// return xhr.responseText;
	// }
	// }
	// }


function handlerResult(that, res, handlerSuccess) {
	handlerSuccess(that, res)
}

// function myCallbackFunction(res) {console.log(res)}

export default function api(link, method, data, that, handlerSuccess=()=>{}) { // async
	serverRequest(link, method, data).then((res) => handlerResult(that, res, handlerSuccess))
	// const res = serverRequest()
	// handlerSuccess(that, res)
	
// 	const link = 'https://weather.api.here.com/weather/1.0/report.json?product=observation&name=Saint-Petersburg&app_id=' + appId + '&app_code=' + appCode // + `&jsoncallback=myCallbackFunction`
// 	// fetch(link).then(res => {console.log('!');res.text().then(data=> {console.log('!!', data)})})

// 	// console.log('!!!')

// 	// const response = await axios({
// 	// 	method: 'get',
// 	// 	url: link,
// 	// 	adapter: jsonpAdapter,
// 	// 	// callbackParamName: 'c' // optional, 'callback' by default
// 	// }).then((res) => {
// 	// 	console.log(res);
// 	// })


// 	fetch(link)  
// 		  .then(  
// 		    function(response) {  
// 		      if (response.status !== 200) {  
// 		        console.log('Looks like there was a problem. Status Code: ' +  response.status);  
// 		        return;  
// 		      }

// 		      // Examine the text in the response  
// 		      response.json().then(function(data) { 
// 		      	// Add the data
		       
// 				console.log(data);
// 		      });  
// 		    }  
// 		  )  
// 		  .catch(function(err) {  
// 		    console.log('Fetch Error :-S', err);  
// });	


}