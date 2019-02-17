import React, {Component} from 'react'

import Header from './Header'
import Body from './Body'
import Footer from './Footer'

// import 'bootstrap/dist/css/bootstrap.css'

class App extends Component {
	state = {
		leftMenu: true,
	}

	render() {
		return (
			<div>
				<Header />
				<Body leftMenu={ this.state.leftMenu }/>
				<Footer />
			</div>
		)
	}
}

export default App