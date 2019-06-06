import api from './api'


// Проверить

export function check(that) {
	return new Promise(function(resolve, reject) {
		const handlerSuccess = (other, res) => {
			resolve(res['result'])
		}

		api(that, 'check', {}, handlerSuccess)
	})
}