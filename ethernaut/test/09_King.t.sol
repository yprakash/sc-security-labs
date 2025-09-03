// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {console, Test} from "forge-std/Test.sol";
import {King} from "../09_King/King.sol";

contract KingTest is Test {
    King public king;
    address public attacker;
    address public deployer;

    function setUp() public {
        attacker = makeAddr("attacker");
        deployer = makeAddr("deployer");
        vm.deal(deployer, 2 ether);
        vm.prank(deployer);
        king = new King{value: 1 ether}();
    }

    function testKingExploit() public {
        // Check initial king
        assertEq(king._king(), deployer, "Deployer should be the initial king");

        // Attacker sends 2 ether to become the new king
        vm.deal(attacker, 2 ether);
        vm.startPrank(attacker);
        (bool success, ) = address(king).call{value: 2 ether}("");
        require(success, "Failed to send ether");
        vm.stopPrank();

        // Check new king
        assertEq(king._king(), attacker, "Attacker should be the new king");
        assertEq(king.prize(), 2 ether, "New prize should be 2 ether");
    }
}