# Ethereum Execution Model
Ethereum’s execution model defines how transactions, smart contracts, and state changes are processed across the decentralized network. Unlike traditional systems, Ethereum must guarantee deterministic results across thousands of nodes, ensuring that everyone agrees on the same global state.

This document explains the execution model step by step, covering its key components, execution process, and the critical topic of concurrency that leads to MEV.

---
## Key Components
### 1. Ethereum Virtual Machine (EVM)
- The **EVM** is a stack-based virtual machine that executes contract bytecode.  
- It is deterministic: given the same input and state, all nodes produce the same output.  
- Runs in a **sandboxed environment** (no direct access to system calls or external processes).

### 2. Smart Contracts
- Programs written in Solidity, Vyper, or other high-level languages.  
- Compiled into EVM bytecode stored at an address.  
- Can maintain state, send ETH, call other contracts, and enforce logic through code.

### 3. Transactions
- Signed messages that can:  
  - Transfer ETH between accounts.  
  - Deploy new contracts.  
  - Call functions on existing contracts.  
- Each transaction is atomic: it either completes fully or reverts.

### 4. Opcodes
- The EVM instruction set (like `ADD`, `SSTORE`, `CALL`, etc.).  
- Contracts are executed by interpreting these opcodes.  
- Developers rarely write opcodes directly, but auditors must understand them.

### 5. Gas
- Every instruction has a **gas cost**.  
- Gas prevents denial-of-service (DoS) attacks by requiring payment for computation.  
- Unused gas is refunded; running out of gas reverts the transaction.

### 6. World State
- A global mapping of all accounts, balances, contract storage, and bytecode.  
- Maintained by all full nodes.  
- Updated deterministically after every transaction.

---
## Process of Execution

### 1. Transaction Submission
- A user signs a transaction and broadcasts it to the **mempool**.  
- It includes: sender, recipient, nonce, gas limit, gas price, and data (for contract calls).  

### 2. Validation
- Validators/miners verify:  
  - The signature is correct.  
  - The sender has enough balance to pay for gas.  
  - The nonce matches the account’s expected count.  

### 3. Execution Context
- When executed, the EVM sets up context variables:  
  - `msg.sender` → who sent the call.  
  - `msg.value` → ETH attached.  
  - `msg.data` → calldata (function selector + arguments).  
  - `block.timestamp`, `block.number`, etc.  

### 4. Bytecode Execution
- The transaction triggers execution of smart contract bytecode.  
- Opcodes are run sequentially, consuming gas.  
- Contracts can call other contracts (`CALL`, `DELEGATECALL`, etc.).

### 5. State Transition
- Execution may read or update the **world state** (balances, storage slots).  
- If execution reverts, all state changes are rolled back.  
- If successful, the state is updated with the transaction’s effects.

### 6. New State Commitment
- After execution, the new world state is committed.  
- Validators/miners record this in the block.  
- Other nodes verify the block’s state transitions before accepting it.

---
## Concurrency and MEV
Ethereum’s EVM executes transactions **sequentially** inside each block. There is **no concurrency or multithreading** within execution: one transaction runs to completion before the next starts.

However, **outside the EVM**, in the mempool, concurrency emerges:
- Multiple users may submit conflicting transactions at the same time.  
- Validators decide the order of inclusion.  
- This lack of guaranteed fairness creates opportunities for **MEV (Maximal Extractable Value).**

### How Transaction Ordering Creates MEV
- **Front-running**: Copying a victim’s profitable trade and executing it first.  
- **Sandwich attacks**: Placing a transaction before and after a victim’s swap to manipulate prices.  
- **Liquidation racing**: Competing to liquidate undercollateralized loans.  

👉 While Ethereum execution itself is sequential, the **competition for transaction ordering in the mempool** introduces a different kind of race — not a code-level race condition, but a *transaction-order–dependent vulnerability*.

---
## Lessons Learned
- Ethereum execution is **atomic and deterministic** inside the EVM.  
- Transactions are processed sequentially, not in parallel.  
- Gas is the metering mechanism that ensures fair resource usage.  
- Security auditors must analyze not only contract logic but also **transaction ordering risks**.  
- MEV is a byproduct of the execution model and mempool dynamics.

---
## References
- [Ethereum.org — Transactions](https://ethereum.org/en/developers/docs/transactions/)  
- [Flashbots MEV Research](https://docs.flashbots.net/)  
