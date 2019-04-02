import React from 'react';

import { getWeather } from '../func/methods'
import './style.css'


export default function Weather() {
	getWeather(this)

	return (
		<div className="weather_block" id="weather"></div>
	)
}