// SPDX-License-Identifier: MIT

// NOTE: This is not yet validated because of 0.6.12 version, but logic should be similar.
pragma solidity ^0.6.12;

import {console, Test} from "forge-std/Test.sol";
import {Reentrance} from "../10_ReEntrancy/Reentrance.sol";
import {ReentranceAttack} from "../10_ReEntrancy/ReentranceAttack.sol";

contract ReEntrancyTest is Test {
    Reentrance public target;
    address public depositor;
    uint256[] public deposit_amounts = [1 ether];
    uint256[] public attack_amounts = [1 ether];
    address public attacker;

    function setUp() public {
        target = new Reentrance();
        attacker = makeAddr("attacker");
        depositor = makeAddr("depositor");
    }

    function testReEntrancy() public {
        uint256 initial_balance = 0;
        uint256 amt = 0;
        for (uint8 i = 0; i < deposit_amounts.length; i++) {
            for (uint8 j = 0; j < attack_amounts.length; j++) {
                vm.deal(depositor, deposit_amounts[i]);
                vm.prank(depositor);
                target.donate{value: deposit_amounts[i]}(address(depositor));

                initial_balance = address(target).balance;
                assert(initial_balance == deposit_amounts[i]);  // attacker found some balance
                amt = attack_amounts[j];
                vm.deal(attacker, amt);
                vm.startPrank(attacker);

                ReentranceAttack hackContract = new ReentranceAttack(address(target), amt);
                assert(initial_balance + amt == address(target).balance);  // Donation done in constructor
                (bool success, ) = hackContract.call("");
                assert(address(target).balance == 0);  // Contract drained

                hackContract.withdrawFunds();
                assert(address(attacker).balance > amt);
                vm.stopPrank();
            }
        }
    }
}