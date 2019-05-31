import React from 'react'

import { appId, appCode } from '../keys'
import { geoLat, geoLng } from '../sets'

import Route from '../Route'


export default function App() {
	return (
		<Route
			app_id={ appId }
			app_code={ appCode }
			lat={ geoLat }
			lng={ geoLng }
			zoom={ 13 }
		/>
	)
}