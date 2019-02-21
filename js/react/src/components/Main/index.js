import React, {Component} from 'react'

import 'bulma/css/bulma.css'
import './style.css'

class Main extends Component {
	state = {
		leftMenu: true
	}

	render() {
		const {handleLeftMenu} = this.props

		return (
			<div id="main">
				<div className="breadcrumb">
					<ul>
						<li><a href="/">Quateo</a></li>
						<li><a href="#">Раздел 1</a></li>
					</ul>
				</div>
				<div>
					<button className="button is-primary is-outlined" onClick={ handleLeftMenu }>Левое меню</button>
				</div>
			</div>
		)
	}
}

export default Main