It is a collection of important/tricky concepts in Solidity, in the form of questions and answers.

----
#### Why `fallback` and `receive` don’t appear in ABI?
- ABI (Application Binary Interface) **lists externally callable functions with names/signatures**.
- `fallback` and `receive` **have no function selector** — they are triggered by the EVM when:
  - `receive()` → plain Ether transfer with empty calldata.
  - `fallback()` → any other call with unknown selector (or non-empty calldata + no match).
- Because they’re **implicit entry points**, they don’t appear in the ABI JSON.
- That’s why they’re easy to miss in an audit — but they can contain critical logic like ownership transfer or fund drain.

---
