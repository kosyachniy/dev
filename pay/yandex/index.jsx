<div className="panel panel_deposit">
	<div className="title">
		Пополнение баланса
		<i className="fas fa-ruble-sign" />
	</div>
	<form method="POST" className="form_deposit" action="https://money.yandex.ru/quickpay/confirm.xml">
		<input type="hidden" name="receiver" value="410019803590042" />
		<input type="hidden" name="quickpay-form" value="donate" />
		<input type="hidden" name="targets" value={`User #${user.id}`} />
		<label>
			<input type="radio" name="paymentType" value="PC" />
			Яндекс.Деньгами
		</label>
		<label>
			<input type="radio" name="paymentType" value="AC" />
			Банковской картой
		</label>
		<input type="number" name="sum" defaultValue="100" data-type="number" />
		<input type="hidden" name="label" value={user.id} />
		<input type="hidden" name="successURL" value="https://tensy.org/profile" />
		<input type="submit" className="btn" value="Пополнить" />
	</form>
</div>