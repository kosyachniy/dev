import api from './api'
import { appId, appCode, place } from '../keys'


export function getWeather(that) {
	const link = 'https://weather.cit.api.here.com/weather/1.0/report.json'

	const data = {
		product: 'observation',
		oneobservation: 'true',
		app_id: appId,
		app_code: appCode,
		name: place,
	}

	const handlerSuccess = (other, res) => {
		console.log(res)
		let div = '<span class="panel"><div><i class="fas fa-thermometer-half"></i> ' +
		res.observations.location[0].observation[0].temperature + ' °C </div><div><i class="fas fa-wind"></i> ' + res.observations.location[0].observation[0].windSpeed + ' ' + res.observations.location[0].observation[0].windDescShort + '</div><div><i class="fas fa-tint"></i> ' + res.observations.location[0].observation[0].humidity  + '%</div></span></br><i class="fas fa-location-arrow"></i> ' + res.observations.location[0].observation[0].city
		document.getElementById('weather').innerHTML = div
	}

	api(link, 'GET', data, that, handlerSuccess)
}