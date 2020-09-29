pragma solidity ^0.6.1;

contract Coin {
    address private minter;
    uint private countCoins = 0;
    mapping (address => uint) private balances;

    constructor(uint initialCoins) public {
        minter = msg.sender;
		countCoins = initialCoins;
		balances[minter] = initialCoins;
    }

	function sendTokens(address user, uint count) public {
		balances[msg.sender] -= count;
		balances[user] += count;
	}

    function getTokens(address user) public view returns (uint) {
        if (msg.sender == minter) {
            return balances[user];
        }
    }
}