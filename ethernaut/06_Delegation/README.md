# Ethernaut Level 06 — Delegation

### Challenge
The goal is to claim ownership of the `Delegation` contract.  
Players must figure out how to manipulate `delegatecall` in the fallback function to overwrite the `owner` variable.

### Vulnerable Logic
```solidity
fallback() external {
    (bool result,) = delegate.delegatecall(msg.data);
    if (result) {
        this;
    }
}
```
### Vulnerability Explained

The fallback function uses `delegatecall` to forward any call to another contract (`Delegate`).  
Because `delegatecall` runs in the caller’s storage context, if the delegated contract has a function that sets `owner = msg.sender`, that assignment will modify the `owner` variable of the `Delegation` contract itself.  
By crafting calldata to trigger this function, an attacker can seize ownership.

### 🚀 Key Takeaways
- `delegatecall` is powerful but dangerous if storage layouts overlap.
- Any exposed function in the delegate contract can be exploited if blindly called.
- Explicitly whitelist which functions can be called.
- Protect critical state variables (owner, admin, etc.) from being modified via delegated calls.
- Always restrict and validate inputs to `delegatecall` usage.

### References
- [Ethernaut Level 6 — Delegation](https://ethernaut.openzeppelin.com/level/0x73379d8B82Fda494ee59555f333DF7D44483fD58)
- [Solidity Docs: delegatecall](https://docs.soliditylang.org/en/latest/introduction-to-smart-contracts.html#delegatecall-and-libraries)
