import React from 'react'
import $ from 'jquery'

import './style.css'

import { events } from './list'
import Point from './Point'


export default class Timeline extends React.Component {
	constructor (props) {
		super(props);
		this.state = {
			nowElement: null
		};
	}

	componentDidMount() {
		setTimeout(() => {
			let time_now = new Date().getTime() / 1000

			let time_list = []
			events.map(point => {
				if (point.time - 2 * 60 * 60 <= time_now) {
					time_list.push(point.time)
				}
			})

			let el = $('#' + Math.max.apply(null, time_list))

			this.setState({ nowElement: Math.max.apply(null, time_list) });

			$('html, body').animate({
				scrollTop: el.offset().top - 70,
			}, 'slow')
		}, 0)
	}

	render() {
		return (
			<div className="card">
			<ul className="timeline">
				{events.map((point, num) => <Point name={point.name} description={point.description} time={point.time} key={num} nowElement={this.state.nowElement} />)}
			</ul>
		</div>
		)
	}
}
