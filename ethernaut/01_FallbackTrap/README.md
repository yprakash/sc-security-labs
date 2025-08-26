# Challenge 01 - FallbackTrap
#### Difficulty: 🟢 Easy
The goal of this level is to become the owner of the contract and drain its balance.

### 📖 Background  
In Solidity, a contract can receive Ether via two special functions: fallback() and receive(). If a contract has a receive() function, it will be triggered when it receives plain Ether with empty calldata. Misusing these functions or combining them with flawed access control logic can lead to critical ownership vulnerabilities.

This level simulates such a real-world issue, encouraging the player to think like both an attacker and an auditor.
