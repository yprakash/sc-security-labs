### Solidity's tuple assignment gas trick
In some Uniswap V2 code, they swap two variables like this to save gas:
```solidity
(a, b) = (b, a);
```
Instead of:
```solidity
uint256 temp = a;
a = b;
b = temp;
```
A junior dev copies this pattern into your protocol.  What’s the main _hidden risk_ of this micro-optimization?

It can cause **silent data corruption** if `a` and `b` are **storage variables of the same slot** (e.g., packed struct fields).

- In Solidity, **tuple assignment evaluates right-hand expressions first**, then writes left-hand variables.  
  But if `a` and `b` are **packed in the same storage slot** (e.g., two `uint128` in a struct), the compiler can overwrite part of the slot prematurely, leading to **data corruption**.
- **Real-world note**: This has bitten people when doing gas packing optimizations — you save gas with smaller types but can break swaps or assignments.
- **Fix**: Manually unpack to temporary variables when working with storage fields in the same slot.
