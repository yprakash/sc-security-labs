# 🧠 EVM-Level Understanding
We’ll explore this in steps:
- EVM Execution Model (stack-based machine)
- Opcodes that matter for security
- Call stack & gas forwarding
- Practical exploit angles

---
## 1. Stack-based Execution
Unlike high-level Solidity, the EVM is a **tiny assembly machine**:
- Every operation works on a **stack** (LIFO).
- Example: `ADD` pops top two numbers, pushes their sum.

So, even something like
```solidity
uint a = 1 + 2;
```
compiles roughly to:
```assembly
PUSH1 0x01
PUSH1 0x02
ADD          // stack now [3]
PUSH1 0x03
```
👉 Auditor’s Angle: If you understand stack flow, you can see where variables are “alive” vs overwritten.

---
## 2. Key Opcodes for Auditors
Let’s highlight **security-relevant ones**:
- `CALL` → external call with **custom gas forwarding**
  - Switches to callee’s code & storage.
  - Execution context: **callee’s storage, caller pays gas**.
  - `msg.sender` = caller.
- `STATICCALL` → read-only external call
  - Same as CALL but **forbids state modifications** (only view).
  - Execution context: callee’s storage, caller pays gas.
- `DELEGATECALL` → runs in caller’s context (state poison risk)
  - Callee’s code runs **inside caller’s storage context**.
  - Execution context: **caller’s storage, caller’s balance**, but **callee’s code**.
  - This is why “library poisoning” is dangerous.
- `CREATE` / `CREATE2` → contract deployment (address predictability)
- `SELFDESTRUCT` → nukes storage, sends ETH

And helpers:
- `SLOAD` / `SSTORE` → storage read/write (gas-sensitive, state integrity)
- `REVERT` → abort execution, refund remaining gas
- `LOGx` → events (don’t affect state, but do affect gas metering)

#### 👉 Mnemonic:
- `CALL` = I send you work & you do it in your house.
- `DELEGATECALL` = I hand you my house keys & you do it inside my house.
- `STATICCALL` = Same as `CALL`, but you’re not allowed to move the furniture.

---
## 3. Call Stack & Gas Forwarding
This is where confusion starts — let’s nail it logically.
- Each external call (`CALL`, `DELEGATECALL`, `STATICCALL`) creates a **new frame** on the call stack.
- Max depth = **1024 frames** → beyond that = failure.

### Gas Rules:
- Before Byzantium: 2300 gas by default for `.send()` / `.transfer()`.
- After EIP-150 (Introduced in 2016 to **prevent DoS** by gas griefing.): “63/64 rule” → callee only gets ~63/64 of gas left
  - When you call another contract with `CALL`/`DELEGATECALL`/etc., the callee only receives  
    63/64ths of the remaining gas (63000, if 64000 gas left & Caller retains 1000 gas).
  - gas_forwarded = min(gas_specified, gas_remaining * 63 / 64)
  - This ensures the caller always keeps a sliver of gas to complete.

#### 👉 Security implication:
You cannot “suicide bomb” the caller by draining all their gas during an external call.

#### 👉 This matters:
- Reentrancy success depends on gas forwarded.
- Denial-of-Service can come from **stack depth limit** (old trick in King of the Ether Throne).

---
## 4. Practical Exploit Angles
Now the fun part — **opcode + stack → exploit thinking**:
1. Stack depth attack (historic, mostly patched):
   - Force the victim to hit 1024 depth so their `send()` always fails.
2. Gas griefing:
   - Attacker contract has fallback that consumes more than 2300 gas → breaks `.transfer()`.
   - Or attacker sets up a scenario where forwarding too much gas causes state inconsistency.
3. DELEGATECALL poisoning:
   - Library function modifies caller’s storage since context is shared.
4. Create2 address precomputation:
   - Attacker can front-run by predicting addresses/contracts before deployment.

---
## 🔹 Quick summary table
| Opcode         | New Frame? | Storage Context | Value Transfer | 63/64 Rule? | Mutability |
| -------------- | ---------- | --------------- | -------------- | ----------- | ---------- |
| `CALL`         | ✅ Yes      | Callee’s        | ✅ Allowed      | ✅ Yes       | Mutable    |
| `STATICCALL`   | ✅ Yes      | Callee’s        | ❌ No           | ✅ Yes       | Immutable  |
| `DELEGATECALL` | ✅ Yes      | Caller’s        | ❌ No           | ✅ Yes       | Mutable    |

---
## 🌰 Nutshell Mental Model
- Stack = scratchpad (temporary values).
- Storage = disk (persistent state).
- Memory = RAM (wiped every tx).
- Call stack = execution nesting, bounded by 1024.
- Gas = execution budget that shrinks on every hop.

If you always ask:
1. Where is data stored (stack, memory, storage)?
2. Who controls execution context (CALL vs DELEGATECALL)?
3. How much gas is forwarded?
4. Can call stack or gas be weaponized?

... you don’t need to memorize — you reason like the EVM.
