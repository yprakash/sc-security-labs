// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

import "./Dependencies.sol";

contract EtherVaultInsecure is ReentrancyGuard {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        require(msg.value > 0, "Deposit must be greater than 0");
        balances[msg.sender] += msg.value;
    }

    function transfer(address _to, uint256 _amount) external {
        if (balances[msg.sender] >= _amount) {
           balances[_to] += _amount;
           balances[msg.sender] -= _amount;
        }
    }

    function withdrawAll() external nonReentrant {
        uint256 balance = getUserBalance(msg.sender);
        require(balance > 0, "Insufficient balance");

        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Failed to send Ether");

        balances[msg.sender] = 0;
    }

    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }

    function getUserBalance(address _user) public view returns (uint256) {
        return balances[_user];
    }
}
