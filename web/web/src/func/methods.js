import api from './api';


// Data

export function getData(that, data={}) {
	const handlerSuccess = (other, res) => {
		console.log(res)
		other.setState({
			cont: JSON.stringify(res),
		})
	}

	api(that, 'data', data, handlerSuccess)
}
