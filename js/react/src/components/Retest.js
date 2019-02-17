import React, {Component} from 'react'

class Retest extends Component {
	state = {
		isOpen: true
	}

	render() {
		const {article} = this.props
		const la = this.state.isOpen && <section>body</section>
		return (
			<div className='test' style={ {color: 'red'} }>
				Component { article.name }
				{ la }
				{ (new Date).toDateString() }
				<button onClick={ this.handleClick }>
					{ this.state.isOpen ? 'tap' : 'untap' }
				</button>
			</div>
		)
	}

	handleClick = () => {
		console.log('Click!')
		this.setState({
			isOpen: !this.state.isOpen
		})
	}
}

export default Retest