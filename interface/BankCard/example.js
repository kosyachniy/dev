import React from 'react'
import CardReactFormContainer from 'card-react'

import './style.css'
import './card.css'

export default class Owner extends React.Component {
	render() {
		return (
			<div className="owner">
				<div className="field main-form">
					<div className="control">
						<input className="input is-primary is-medium" type="text" placeholder="Where are your home?" />
					</div>

					<div className="control">
						<input className="input is-primary is-medium" type="text" placeholder="Phone" />
					</div>
				</div>

				<CardReactFormContainer
					container="card-wrapper"
					formInputsNames={
						{
							number: 'CCnumber', // optional — default "number"
							expiry: 'CCexpiry',// optional — default "expiry"
							cvc: 'CCcvc', // optional — default "cvc"
							name: 'CCname' // optional - default "name"
						}
					}

					initialValues= {
						{
							// number: '4242424242424242', // optional — default •••• •••• •••• ••••
							// cvc: '888', // optional — default •••
							// expiry: '08/20', // optional — default ••/••
							// name: 'Poloz Alexey' // optional — default FULL NAME
						}
					}

					classes={
						{
							valid: 'valid-input', // optional — default 'jp-card-valid'
							invalid: 'invalid-input' // optional — default 'jp-card-invalid'
						}
					}

					formatting={true} // optional - default true
				>
					<div className="field has-addons">
						<div className="control">
							<input placeholder="Card number" type="text" name="CCnumber" className="input is-primary is-medium" />
						</div>
						<div className="control is-half">
							<input placeholder="Full name" type="text" name="CCname" className="input is-primary is-medium" />
						</div>
						<div className="control">
							<input placeholder="MM/YY" type="text" name="CCexpiry" className="input is-primary is-medium" />
						</div>
						<div className="control">
							<input placeholder="CVC" type="text" name="CCcvc" className="input is-primary is-medium" />
						</div>
					</div>
				</CardReactFormContainer>

				<div id="card-wrapper"></div>
			
				<div className="field">
					<button className="button is-primary is-fullwidth" onClick={ this.props.handlerSubmit }>Confirm</button>
				</div>
			</div>
		)
	}
}