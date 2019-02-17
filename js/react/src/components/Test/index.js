import React from 'react'
import './style.css'

function Test(props) {
	const {article} = props
	const la = <section>body</section>
	return (
		<div className='test' style={ {color: 'red'} }>
			Component { article.name }
			{ la }
			{ (new Date).toDateString() }
			<button onClick={ handleClick }>tap</button>
		</div>
	)
}

function handleClick() {
	console.log('Click!')
}

export default Test