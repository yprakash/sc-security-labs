### Constant expressions & gas
```solidity
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract ConstGasSavings {
    uint256 public constant FEE = 3;
    uint256 public fee = 3;

    function calcFEE(uint256 x) public pure returns (uint256) {
        return x * FEE;
    }

    function calcFee(uint256 x) public view returns (uint256) {
        return x * fee;
    }
}
```
Why is `calcFEE()` generally cheaper than `calcFee()`?  
- Because `constant` variables don’t exist in storage — they’re inlined at compile time. they don’t occupy a storage slot at all.
- This means accessing them costs **0 gas** beyond the base instruction, because the compiler literally replaces `FEE` with `3` in the bytecode.
- In contrast, `fee` is a storage variable, so reading it costs an **SLOAD** (~2,100 gas first read, ~100 gas subsequent reads in the same transaction).

**Security angle**:  
If a value never changes, making it `constant` not only saves gas but also prevents accidental or malicious modification.  
However, for upgradeable contracts, constants can’t be “upgraded” — which means hardcoding them can cause long-term inflexibility if the logic needs to adapt.
