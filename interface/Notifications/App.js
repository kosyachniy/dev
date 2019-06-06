import React from 'react'
import $ from 'jquery'
import ion from 'ion-sound'

import { check } from './func/methods'


function realtimeGet() {
	setInterval(function() {
		check().then((res) => {
			if (res) {
				clearInterval()

				$('body').append('<div class="notification"></div>')
				$('.notification').append('<div class="text">New request</div>')

				window.ion.sound({
					sounds: [
						{name: "button_click"},
					],
					path: "/sounds/",
					preload: true,
					volume: 1.0,
				})

				window.ion.sound.play('button_click')
			}
		})
	}, 1000)
}

export default class App extends React.Component {
	componentDidMount() {
		realtimeGet()
	}

	render() {
		return (
			<div></div>
		)
	}
}