import React, {Component} from 'react'

import 'bulma/css/bulma.css'
import './style.css'

export default class Footer extends Component {
	render() {
		return (
			<div className="footer container">
				<div className="columns">
					<div className="column is-3">
					Колонка 1
					</div>

					<div className="column is-3">
					Колонка 2
					</div>

					<div className="column is-6">
					Колонка 3
					</div>
				</div>
			</div>
		)
	}
}