import React from 'react'
import Test from './Retest'
import 'bulma/css/bulma.css'
// import 'bootstrap/dist/css/bootstrap.css'

function App() {
	return (
		<div>
			<h1>Main</h1>
			<Test article={ {name: 'article name', cont: 'article cont'} }/>
		</div>
	)
}

export default App