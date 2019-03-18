import React from 'react'

import LeftMenu from '../LeftMenu'
import Main from '../Main'
import RightMenu from '../RightMenu'

import 'bulma/css/bulma.css'
import './style.css'

class Body extends React.Component {
	state = {
		leftMenu: this.props.leftMenu,
	}

	render() {
		const leftMenu = this.state.leftMenu && <div className="column is-one-fifth"><LeftMenu /></div>

		return (
			<div className="container has-background-white" id="body">
				<div className="columns">
					{ leftMenu }

					<div className="column">
						<Main handleLeftMenu={ this.handleLeftMenu } />
					</div>

					<div className="column is-one-fifth">
						<RightMenu />
					</div>
				</div>
			</div>
		)
	}

	handleLeftMenu = () => {
		this.setState({
			leftMenu: !this.state.leftMenu
		})
	}
}

export default Body