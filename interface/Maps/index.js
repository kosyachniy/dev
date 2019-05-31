import React from 'react'

import { getGeo } from '../func/methods'


export default class Map extends React.Component {
	constructor(props) {
		super(props)

		this.platform = null
		this.map = null
		this.state = {
			app_id: props.app_id,
			app_code: props.app_code,
			center: {
				lat: props.lat,
				lng: props.lng,
			},
			zoom: props.zoom,
			search: props.search,
			markers: props.markers,
			// theme: props.theme,
			// style: props.style,
			lat: null,
			lng: null,
		}
	}

	componentDidMount() {
		// function addMarkersToMap(map, lat, lng) {
		// 	let parisMarker = new window.H.map.Marker({lat, lng});
		// 	map.addObject(parisMarker);
		// }

		this.platform = new window.H.service.Platform({
            app_id: this.props.app_id,
            app_code: this.props.app_code,
            // useCIT: true,
            useHTTPS: true,
        })

        let pixelRatio = window.devicePixelRatio || 1
		let layer = this.platform.createDefaultLayers({
            tileSize: pixelRatio === 1 ? 256 : 512,
            ppi: pixelRatio === 1 ? undefined : 320
        })
		let container = document.getElementById('here-map')
		container.style = 'height: 100vh'

		this.map = new window.H.Map(container, layer.normal.xbase, {
			center: this.state.center,
            zoom: this.state.zoom,
            pixelRatio
		})

		let events = new window.H.mapevents.MapEvents(this.map)
		// eslint-disable-next-line
		let behavior = new window.H.mapevents.Behavior(events)
		// eslint-disable-next-line
		let ui = new window.H.ui.UI.createDefault(this.map, layer)

		// addMarkersToMap(this.map, 50.086882, 14.4203952)

		getGeo(this) // , {'search': this.props.search})
		

		// window.navigator.geolocation.getCurrentPosition(
		// 	(position) => {
		// 		this.setState({
		// 			lat: position.coords.latitude,
		// 			lng: position.coords.longitude,
		// 		})

		// 		// console.log(this.state.lat, this.state.lng)

		// 		addMarkersToMap(this.map, this.state.lat, this.state.lng)
		// 	}
		// )
	}

	render() {
		return (
			<div id="here-map" style={ {
							width: '100%',
							height: '100%',
							background: 'grey',
						} } />
		)
	}
}