//SPDX-License-Identifier: MIT

pragma solidity 0.8.15;

contract Main {
    bool valBool;
    int valInt;
    uint8 valUint = 1;
    string public valStr; // ASCII
    string valStr2 = unicode"😄"; // Unicode
    string public valStr3 = hex"4B"; // HEX
    address public valAdr;

    bool public resEq = valInt == 0;
    bool public resNe = !valBool;
    bool public resNeq = valInt != 0;
    bool public resAnd = resNeq && resNe;
    bool public resOr = valBool || resNeq;
    bool public resLess = 5 < 7;
    bool public resLessEq = valUint >= 1;
    int public resBand = 5 & 7;
    int public resBor = 5 | 7;
    int public resBxor = 5 ^ 7;
    int public resBne = ~7;
    int public resLshift = 5 << 7;
    int public resRshift = 5 >> 7;
    // int public resDiv = 7 / 5;
    int public resMod = 7 % 5;
    int public resPlus = 7 + 5;
    int public resMinus = 5 - 7;
    int public resMul = 5 * 7;
    uint public resDegree = 2 ** 255;
    string public valConc = string.concat(valStr, valStr2, valStr3);

    // public / private / internal / external
    // pure / constant / view / payable
    // function getResult() public {
    //     resDegree *= 2;
    // }
}
