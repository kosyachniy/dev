import React from 'react';

import { getData } from '../../../func/methods'


export default class App extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			cont: 'loading',
		}
	}

	componentDidMount() {
		getData(this, {'param': 'qwerty'})
	}

	render() {
		return (
			<>
				<div>{ this.state.cont }</div>
			</>
		)
	}
}
