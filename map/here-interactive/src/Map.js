import React from 'react'


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
			// theme: props.theme,
			// style: props.style,
		}
	}

	componentDidMount() {
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
