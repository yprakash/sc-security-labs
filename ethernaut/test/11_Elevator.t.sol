// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "../11_Elevator/Elevator.sol";
import "../11_Elevator/BuildingFloor.sol";
import {console, Test} from "forge-std/Test.sol";

contract ElevatorTest is Test {
    Elevator public elevator;

    function setUp() public {
        elevator = new Elevator();
    }

    function testElevatorExploit() public {
        assertFalse(elevator.top());
        console.log("Checked elevator.top=", elevator.top());
        BuildingFloor attacker = new BuildingFloor(address(elevator));
        attacker.attack();
        assertTrue(elevator.top());
        console.log("Checked elevator.top=", elevator.top());
    }
}