//SPDX-License-Identifier: MIT

pragma solidity 0.8.18;

/**
* @title The Coin
* @dev Example of coin smartcontract
* @custom:dev-run-script ./script.ts
*/

contract Coin {
    address private minter;
    uint private countCoins = 0;
    mapping (address => uint) private balances;

    constructor(uint initialCoins) {
        minter = msg.sender;
        countCoins = initialCoins;
        balances[minter] = initialCoins;
    }

    function sendTokens(address user, uint count) public {
        balances[msg.sender] -= count;
        balances[user] += count;
    }

    function getTokens(address user) public view returns (uint count) {
        if (msg.sender == minter) {
            return balances[user];
        }
    }
}
