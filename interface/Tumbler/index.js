import React from 'react'

import './style.css'


export default class Header extends React.Component {
	render() {
		return (
			<div className="header">
				<div className="trig">
					<font>Подборка</font>
					<label className="switch">
						<input type="checkbox" onChange={ this.props.handlerType } />
						<span className="slider round"></span>
					</label>
					<font>Карта</font>
				</div>
			</div>
		)
	}
}