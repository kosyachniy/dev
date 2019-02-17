import React, {Component} from 'react'

import LeftMenu from '../LeftMenu'
import Main from '../Main'
import RightMenu from '../RightMenu'

import 'bulma/css/bulma.css'
import './style.css'

class Body extends Component {
	state = {
		leftMenu: this.props.leftMenu,
	}

	render() {
		const leftMenu = this.state.leftMenu && <div className="column"><LeftMenu /></div>

		return (
			<div className="container">
				<div class="columns">
					{ leftMenu }

					<div className="column is-three-fifths">
						<Main />
					</div>

					<div className="column">
						<RightMenu />
					</div>
				</div>
			</div>
		)
	}
}

export default Body