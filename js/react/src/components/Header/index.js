import React from 'react'

import 'bulma/css/bulma.css'
import './style.css'

function Header() {
	return (
		<div className="has-background-white">
			<div className="navbar has-shadow container" id="header">
				<div className="navbar-brand">
					<a className="navbar-item" href="/">
						Quateo
					</a>
				</div>
				<div className="navbar-menu">
					<div className="navbar-start">
						<a className="navbar-item" href="#">
							Ссылка 1
						</a>
						<a className="navbar-item" href="#">
							Ссылка 2
						</a>
					</div>
					<div className="navbar-end">
						<a className="navbar-item" href="#">
						Войти
						</a>
					</div>
				</div>
			</div>
		</div>
	)
}

export default Header