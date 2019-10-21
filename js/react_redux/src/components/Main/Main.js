import React from 'react';


function App(props) {
  return (
	<div
		className="App"
		onClick={ props.activateGeod({ title: 'I am a geo dude!' })}
	>
		{ props.geod.title || 'Pusto!' }
	</div>
  );
}

export default App;
