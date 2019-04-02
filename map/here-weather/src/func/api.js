import $ from 'jquery'


function serverRequest(link, method, data) {
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

function handlerResult(that, res, handlerSuccess) {
	handlerSuccess(that, res)
}

export default function api(link, method, data, that, handlerSuccess=()=>{}) {
	serverRequest(link, method, data).then((res) => handlerResult(that, res, handlerSuccess))
}