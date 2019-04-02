import React from 'react';

import { appId, appCode, geoLat, geoLng } from './keys'
import Map from './Map'


export default class App extends React.Component {
	render() {
		return (
			<Map
				app_id={ appId }
				app_code={ appCode }
				lat={ geoLat }
				lng={ geoLng }
				zoom={ 11 }
			/>
		)
	}
}