// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {console, Test} from "forge-std/Test.sol";
import "../13_GatekeeperOne/GatekeeperOne.sol";
import "../13_GatekeeperOne/GatekeeperOneAttacker1.sol";

contract GatekeeperOneTest is Test {
    GatekeeperOne public gatekeeper;
    GatekeeperOneAttacker1 public attackContract;
    address public deployer = address(0xBEEF);
    address public attackerEOA = address(0x1337);

    function setUp() public {
        vm.startPrank(deployer);
        gatekeeper = new GatekeeperOne();
        vm.stopPrank();
    }

    function testGatekeeperOneExploit() public {
        vm.startPrank(attackerEOA);
        attackContract = new GatekeeperOneAttacker1(address(gatekeeper));
        (uint256 attempts, uint256 gasUsed) = attackContract.attack();
        console.log("Attempts:", attempts);
        console.log("Successful gas:", gasUsed);
        vm.stopPrank();
        // assertEq(gatekeeper.entrant(), attackerEOA, "Exploit failed: attacker is not the entrant");
    }
}