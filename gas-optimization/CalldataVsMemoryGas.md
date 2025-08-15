### Calldata vs. memory arrays — gas heavy loop
```solidity
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract CalldataVsMemoryGas {
    function process(uint256[] memory arr) public pure returns (uint256 sum) {
        for (uint256 i = 0; i < arr.length; i++) {
            sum += arr[i];
        }
    }
}
```
If `arr` comes from a transaction input and is read-only inside the loop, what’s the **most gas-efficient** change?

Change to `calldata`
```solidity
function process(uint256[] calldata arr) public pure returns (uint256 sum) {
    for (uint256 i = 0; i < arr.length; i++) {
        sum += arr[i];
    }
}
```
- `memory` parameters require a **full copy** from calldata into memory when the function starts.
- `calldata` parameters are **read-only** and accessed directly from the transaction payload — no copy needed.
- For large arrays, avoiding the copy can save thousands of gas.

**Extra benefit**: `calldata` also makes your intent explicit — the array won’t be mutated.

**Security note**: While `calldata` saves gas, in low-level assembly parsing, you must handle the layout carefully — wrong offset math can read garbage data, which could be exploited in crafted calldata-based attacks.
