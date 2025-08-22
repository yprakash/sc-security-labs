# EVM Call Failure Modes: Revert, OutOfGas, and Beyond
Smart contract developers often assume that a `CALL` either succeeds or reverts.  
But under the hood, the EVM has several *different* failure modes that auditors must distinguish.

---
## 1. When Callee Explicitly Reverts
Example:
```solidity
fallback() external payable {
    revert("nope");
}
```
- The `REVERT` opcode returns error data to the caller.
- Caller behavior depends on how the call was made:
  - `transfer`: bubbles up → caller **reverts**.
  - `send`: swallows revert → caller gets `false`.
  - `call`: returns `(false, returndata)`.

👉 **Key point**: explicit revert = callee fails with revert reason.

---
## 2. When Callee Consumes All Gas
Example:
```solidity
fallback() external payable {
    while (true) {} // infinite loop burns all gas
}
```
- The EVM halts execution with **OutOfGas (OOG)**.
- Unlike **REVERT**, no return data is produced.
- From caller’s perspective:
  - `transfer`: reverts (since it uses all 2300 gas stipend).
  - `send`: returns `false`.
  - `call`: returns `(false, "")`.

👉 **Key point**: OOG = exception = callee fails, caller sees failure.

---
## 3. What About StackTooDeep?
`StackTooDeep` errors come from the Solidity compiler when a function exceeds the 16-slot EVM stack limit.
```vbnet
CompilerError: Stack too deep, try removing local variables.
```
- This is **compile-time only**, never a runtime failure: caused by Solidity mapping too many
  local variables/parameters into the 16-slot calling convention that the compiler uses internally.
- This happens **before deployment**, not something an attacker can trigger.
- Contracts with this issue cannot even be deployed.
- Not to be confused with runtime generic “stack overflow” at the EVM level

👉 **Key point**: don’t confuse compile-time `StackTooDeep` with runtime call failures.

---
## 4. Runtime Stack Overflow
Happens when recursion or deeply nested calls blow the stack at runtime.
- If the call depth exceeds 1024 → EVM halts with a failure (similar to OOG).
- But this is tracked as `CALLDEPTH` **limit violation** or “stack overflow”, not the Solidity compiler’s `StackTooDeep`.

---
### 📑 The Taxonomy Table
| **Failure Mode**               | **Layer**                     | **Cause**                                                    | **How it surfaces in Solidity**                                      | **Auditor’s Note**                                                                                                     |
| ------------------------------ | ----------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Out-of-Gas (OOG)**           | Runtime (EVM)                 | Callee runs out of allocated gas mid-execution.              | `success == false`; revert-like.                                     | Gas-heavy external calls (loops, dynamic arrays). Can be induced by attacker contracts with deliberately costly logic. |
| **Revert / Invalid opcode**    | Runtime (EVM)                 | Callee executes `REVERT`, `INVALID`, or `assert(false)`.     | `success == false`; revert reason may or may not be available.       | Cannot be distinguished from OOG at Solidity level unless you parse returndata. Core of many DoS patterns.             |
| **CALLDEPTH exceeded**         | Runtime (EVM)                 | Call stack >1024 frames.                                     | `success == false` instantly, without starting callee execution.     | Rare today, but was weaponized in 2016 Shanghai DoS. Still conceptually important.                                     |
| **Return-data-too-large**      | Runtime (EVM, post-Byzantium) | Callee returns more data than caller’s buffer size.          | EVM truncates data; may look like incomplete returndata in Solidity. | Not fatal per se, but dangerous if protocol assumes complete data integrity (e.g. ABI decoding).                       |
| **Stack underflow / overflow** | Runtime (EVM)                 | Invalid stack operations (push/pop mismatch).                | Immediate `INVALID` → same surface as revert.                        | Normally avoided by Solidity compiler. Only arises in hand-written assembly.                                           |
| **Compile-time StackTooDeep**  | Compiler (Solc)               | More than 16 stack variables at once.                        | Fails compilation: `StackTooDeep` error.                             | Not a runtime issue. Shouldn’t be confused with CALLDEPTH.                                                             |
| **Precompile call failure**    | Runtime (EVM)                 | Call to precompile fails (e.g. wrong input, not enough gas). | `success == false`.                                                  | Auditor must check precompile usage (BN254, SHA256, etc.). Gas assumptions matter.                                     |

---
### 📌 Takeaway
- Always ask: “**How does this call fail, and what does the caller do with that failure?**”
- Explicit `REVERT` and OOG both fail the callee, but the caller’s handling (bubble up vs swallow) depends on the call type (transfer, send, call).
- Don’t overthink `StackTooDeep`: it’s just a compiler guard, not an attack vector.
