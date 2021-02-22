const {
	createAccount, createToken, buyToken, burnToken,
	getBalance, getTokenBalance, transfer, getToken,
} = require("./hts");
require("dotenv").config();


const treasuryAccountId = process.env.ACCOUNT_ID;
const treasuryPrivateKey = process.env.PRIVATE_KEY;


async function main() {
	const [accId, accKey] = await createAccount();
	console.log(accId, accKey);

	const token = await createToken("Token", "TOK");
	console.log(token);

	const balance_transfer = await transfer(treasuryAccountId, "0.0.307141", treasuryPrivateKey);
	console.log(balance_transfer);

	const transaction_buy = await buyToken("0.0.305536", 1, "0.0.307141", "302e020100300506032b6570042204201b00250e3e1892eba8f81ee42b401354095bc59e2017c4942b6be8daf7a76844");
	console.log(transaction_buy);

	const transaction_burn = await burnToken("0.0.305536", 1, "0.0.307141", "302e020100300506032b6570042204201b00250e3e1892eba8f81ee42b401354095bc59e2017c4942b6be8daf7a76844");
	console.log(transaction_burn);

	const balance = await getBalance("0.0.307141");
	console.log(balance);

	const balance_token = await getTokenBalance("0.0.307141");
	console.log(balance_token);

	const token_info = await getToken("0.0.305536");
	console.log(token_info);
}

main();