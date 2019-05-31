import React from 'react'
import { Link } from "react-router-dom"

import './style.css'


export default class Bar extends React.Component {
	render() {
		return (
			<div className="tabbar">
				<Link to="/timeline"><i className="fas fa-calendar-alt"></i></Link>
				<Link to="/services"><img src="/img/logo.png"/></Link>
				<Link to="/map/density"><i className="fas fa-map"></i></Link>
			</div>
		)
	}
}