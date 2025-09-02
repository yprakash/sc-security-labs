# Ethernaut Level 04 - Telephone
### Overview
This level highlights the danger of using `tx.origin` for authorization. Contracts that rely on it can be tricked when calls are made through another contract.

### Vulnerable Code
```solidity
function changeOwner(address _owner) public {
    if (tx.origin != msg.sender) {
        owner = _owner;
    }
}
```
### Essence of the Vulnerability
`tx.origin` is the **original external account** that started the transaction. If authorization is based on it, an attacker can deploy a malicious contract that makes the victim call into this function, thereby bypassing ownership restrictions.

### Lessons Learned
- Always use `msg.sender` (the immediate caller) for access control.
- `tx.origin` should almost never be used in authorization logic.
- Be wary of phishing-style attacks where victims are tricked into initiating a transaction.
