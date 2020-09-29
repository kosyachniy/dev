pragma solidity ^0.6.1;

contract Coin {
    address private minter;
    address private notary;
    uint private countCoins = 0;
    mapping (address => uint) private balances; // Баланс токенов

    event MintCoins (
        address owner,
        uint count
    );

	event SendCoins (
		address sender,
		address recipient,
		uint count
	);

    constructor(uint initialCoins) public {
        minter = msg.sender; // Чеканщик - создание токенов
        notary = msg.sender; // Нотариус - распределение активов

		countCoins = initialCoins;
		balances[minter] = initialCoins;

		emit MintCoins(minter, initialCoins);
    }

    // Добавление монет

    function mintTokens(address user, uint count) public {
        if (msg.sender == minter) {
            balances[user] += count;
            countCoins += count;

			emit MintCoins(minter, count);
        }
    }

	// Отправить монеты

	function sendTokens(address user, uint count) public {
		balances[msg.sender] -= count;
		balances[user] += count;

		emit SendCoins(msg.sender, user, count);
	}

    // Проверка баланса

    function getTokens(address user) public view returns (uint) {
        if (msg.sender == minter) {
            return balances[user];
        }
    }
}