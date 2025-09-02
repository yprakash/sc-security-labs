# Ethernaut Level 05 — Token
### Overview
This challenge demonstrates how improper use of arithmetic in Solidity can lead to **integer underflow**, allowing attackers to mint more tokens than intended.

### Vulnerable Logic
```solidity
function transfer(address _to, uint _value) public returns (bool) {
    require(balances[msg.sender] >= _value);
    balances[msg.sender] -= _value;   // underflow possible
    balances[_to] += _value;
    return true;
}
```
### Vulnerability Explained
- Before Solidity 0.8, arithmetic operations did not automatically check for overflow/underflow.
If balances[msg.sender] < _value, subtracting causes an underflow, wrapping the balance to a very large number. This effectively gives the attacker more tokens than they should have.

### Lessons Learned
- Always use Solidity ≥0.8, which has built-in overflow/underflow checks.
- Alternatively, use libraries like OpenZeppelin’s SafeMath for arithmetic safety.
- Token contracts must enforce strict balance accounting to prevent inflation exploits.
