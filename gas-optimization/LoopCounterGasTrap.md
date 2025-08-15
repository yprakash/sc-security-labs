### uint8 loop counter gas trap
This is a gas trap that can be used to limit the number of iterations in a loop. It uses a `uint8` variable to count the number of iterations and will revert if the count exceeds a specified limit.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract GasTrap {
    uint256 public counter;

    function increment(uint256 n) external {
        for (uint256 i = 0; i < n; ) {
            counter += 1;
            unchecked { i++; }
        }
    }
}
```
What happens is we **change** `uint256 i = 0;` to `uint8 i = 0;` to save gas in the loop counter?

This change may increase gas because the compiler inserts extra masking for `uint8` in storage/memory.
- Even though `uint8` is smaller in size, Solidity stores local variables like loop counters on the **EVM stack**, which is a 256-bit machine.
- When you use `uint8`, the compiler must insert **extra** `AND 0xff` **masking instructions** every time it’s read or written, which can **increase gas** compared to using the native `uint256`.

**Key takeaway**:  
- Gas optimization in Solidity is often _counterintuitive_.
- For local variables (loop counters, function args, temporary vars), use `uint256` unless you have a _real_ packing benefit in storage.
