What happens if an EVM contract executes `CALL` when the call stack is already at maximum depth (1024)?  
A. The EVM throws `INVALID` opcode error  
B. The call is ignored, execution continues, and `success = false`  
C. The entire transaction reverts  
D. The caller runs out of gas immediately
> B
- At depth 1024, a further `CALL`/`DELEGATECALL`/`STATICCALL` **does not execute** the callee. The EVM immediately returns `success = 0` to the caller. No revert is thrown automatically, so the **transaction does not auto-revert** unless the caller checks `success` and reverts.
- Why not C? Because the failure is local to that call; the caller can choose to continue.

---
Which of the following **does NOT consume gas** directly in the EVM?  
A. `JUMPDEST`  
B. `STOP`  
C. `RETURN`  
D. `REVERT`
> B (with nuance)
- `JUMPDEST` does cost (1 gas).
- `STOP`, `RETURN`, `REVERT` have **0 base cost** (though **memory expansion** for `RETURN`/`REVERT` data still costs gas).

---
During a `DELEGATECALL`, which of the following is inherited from the caller and NOT taken from the callee?  
A. Storage  
B. Code  
C. Address (`msg.sender`)  
D. Balance (`address(this).balance`)
> A, C, D

---
Consider this sequence:
```solidity
PUSH1 0x0
SSTORE
```
What is the outcome?  
A. Writes `0x0` into storage slot `0x0`  
B. Causes stack underflow → `INVALID`  
C. Writes empty data and refunds gas  
D. Reverts automatically
> B
- `SSTORE` needs **two stack items**: `value` and `slot` (top-of-stack is the slot).
- With only one `PUSH1`, you get a **stack underflow** → `INVALID` (halt).
- Correct sequence to store 0 into slot 0 would be:
```solidity
PUSH1 0x00   // value
PUSH1 0x00   // slot
SSTORE
```
---
At the opcode level, what happens when a contract executes `SELFDESTRUCT`?  
A. All storage is immediately zeroed out  
B. Balance is transferred, code removed at end of transaction  
C. Code is erased mid-execution, halting current call  
D. Remaining gas is refunded fully
> Mostly B, with EIP-6780 caveat
- Pre-Shanghai (old): Balance transferred; account’s code & storage removed **at end of tx** → matches B.
- Post-Shanghai / EIP-6780 (current):
  - If the contract was not created in the same transaction, `SELFDESTRUCT` **does not delete code/storage**; it primarily **transfers balance** and zeroes the account’s balance.
  - Deletion only applies for contracts **created and destroyed within the same tx**.
- Auditing takeaway: do not rely on `SELFDESTRUCT` **to “clean up”** contracts anymore.

---
Which opcode introduces new call frames on the EVM call stack?  
A. `CALL`, `CREATE`, `DELEGATECALL`, `STATICCALL`  
B. `JUMP`, `JUMPI`  
C. `SSTORE`, `MSTORE`  
D. `LOG0` ... `LOG4`
> A
- `CALL`, `DELEGATECALL`, `STATICCALL`, `CREATE` (and `CREATE2`) all push new frames.
- All others do **not** create frames; they are intra-frame control flow.

---
If returndata size exceeds the caller’s allocated memory buffer in `CALL`, how does EVM behave?  
A. Transaction reverts  
B. Excess is truncated, caller only gets what fits  
C. Overflow is written to next memory page  
D. The call silently fails with `success = false`
> B
- Callee can return more bytes than the caller allocated. The EVM **truncates** the copy to the provided buffer size.
- The call **does not fail** because of oversized return data. This **matters for ABI decoding**: always check lengths.

---
Which of the following is TRUE about `STATICCALL`?  
A. Cannot alter storage, but can emit events  
B. Cannot alter storage or log events  
C. Can alter storage if delegatecalled  
D. Can create new contracts with `CREATE`
> B
- In a **static** context you **cannot**:
  - Modify storage (SSTORE),
  - Emit logs (LOG0 ... LOG4),
  - Create/Destroy contracts (`CREATE`, `CREATE2`, `SELFDESTRUCT`).
- So: **no storage writes and no events**.

---
When the EVM executes `JUMP` to a destination without `JUMPDEST`, what occurs?  
A. Execution continues but ignores the jump  
B. Execution halts with `INVALID`  
C. Execution reverts with returndata = `0x`  
D. Treated as `STOP`
> B
- Jumping to a byte offset that isn’t a `JUMPDEST` causes an `INVALID` (halt).
- It’s not treated like `STOP`; the VM enforces structured control flow via `JUMPDEST`.

---
Why are `CALL` failures in Solidity (`success == false`) indistinguishable between Out-of-Gas and Revert?  
A. Because both return empty returndata and set `success=false`  
B. Because the EVM truncates returndata always  
C. Because `CALL` always returns `true` unless callee explicitly reverts  
D. Because OOG propagates as `assert` failures
> Mostly A (with a caveat)
- From Solidity’s common pattern:
    ```solidity
    (bool ok, bytes memory data) = target.call(payload);
    if (!ok) { ... }
    ```
  you **can’t tell** if failure was OOG vs REVERT unless you inspect/interpret returndata.
- Caveat: `REVERT` **can include revert data; OOG won’t**. Answer A: “both return empty returndata” — not always true. The indistinguishability comes from code often only checking ok and treating both paths identically.
