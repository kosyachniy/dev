import React from 'react';
import { BrowserRouter, Route, Switch } from 'react-router-dom';

import Body from './Structure/Body';


export default class App extends React.Component {
	render() {
		return (
			<>
				<BrowserRouter>
					<Switch>
						<Route exact path="/">
							<Body />
						</Route>
					</Switch>
				</BrowserRouter>
			</>
		)
	}
}
