### Gas Optimization + Reentrancy Risk
You’re optimizing this ERC-20 withdrawal logic:
```solidity
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract GasOptimizedNonReentrant {
    mapping(address => uint256) public balanceOf;

    function withdraw(uint256 amount) external {
        require(balanceOf[msg.sender] >= amount, "Not enough balance");

        // External call
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        // State update
        balanceOf[msg.sender] -= amount;
    }
}
```
Which **single change** both improves gas efficiency **and** reduces reentrancy risk?  
Swap the order — update `balanceOf` **before** calling `msg.sender`.

- **Gas efficiency**: Writing to storage (`balanceOf`) before the external call means if the external call fails, the revert will undo it anyway. But importantly, it **reduces the number of expensive SLOAD/SSTORE operations in some patterns**.
- **Security**: This follows the **Checks-Effects-Interactions** pattern — updating state before an external call prevents reentrancy from exploiting stale balances.
