import React, { useState, useEffect } from 'react';
import { BrowserRouter, Route, Switch } from 'react-router-dom';

import api from './func/api';


const App = () => {
	const [cont, setCont] = useState('loading')

	useEffect(() => {
		api('posts.get', {id: 1}, (res) => {
			setCont(JSON.stringify(res))
		})
	}, [])

	return (
		<>
			<BrowserRouter>
				<Switch>
					<Route exact path="/">
						<div>{ cont }</div>
					</Route>
				</Switch>
			</BrowserRouter>
		</>
	)
}

export default App;