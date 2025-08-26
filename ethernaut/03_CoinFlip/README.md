# Challenge 03 - Coin Flip
### Overview
This level demonstrates the danger of using predictable on-chain values for randomness. The contract relies on `blockhash` and block properties, which are deterministic and exploitable.

### Vulnerable Code
```solidity
uint256 blockValue = uint256(blockhash(block.number - 1));
uint256 coinFlip = blockValue / FACTOR;
bool side = coinFlip == 1;
```
### Essence of the Vulnerability
Randomness derived directly from blockchain state (like blockhash) is not random. Attackers can compute the exact outcome off-chain and always win by calling the function with the correct guess.

### Lessons Learned
- Never use `blockhash`, `block.timestamp`, or similar values for randomness.
- Use a verifiable randomness source such as Chainlink VRF
- Deterministic blockchain data is predictable and should not secure games of chance.
