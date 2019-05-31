import React from 'react'

import { appId, appCode } from '../../keys'

import Map from './Maps'


export default function App() {
	return (
		<Map
			app_id={ appId }
			app_code={ appCode }
			lat={ viewer.geoLat }
			lng={ viewer.geoLng }
			zoom={ viewer.zoom }
			search={ this.state.search }
			markers={ this.state.markers }
			// markerLat={ this.state.lat }
			// marletLng={ this.state.lng }
		/>
	)
}