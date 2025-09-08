# Ephemeral Contracts in Trading & Flash Loans

A common idea in DeFi is to create an **ephemeral contract** — a smart contract that is deployed, executes some profitable action (like a flash loan + arbitrage), and then destroys itself using `selfdestruct`. At first glance, this looks like a stealth technique: the contract exists only briefly and then disappears from the blockchain state.  

But does this actually hide your strategy from miners, validators, or MEV bots? Let’s break it down.

---
### 1. What Are Ephemeral Contracts?
- An **ephemeral contract** is deployed solely to perform one or a few actions and then immediately calls:
  ```solidity
  selfdestruct(payable(msg.sender));
  ```
- This removes the contract’s bytecode and storage from the blockchain state after execution.
- The creator receives any leftover ETH in the contract.

**Intended benefit**: The contract doesn’t leave behind an on-chain footprint for others to copy.

---
### 2. Mempool Visibility
- Before inclusion in a block, every transaction sits in the **public mempool**.
- Validators and bots can see:
  - The contract creation bytecode (constructor + logic).
  - The calldata for function calls (flash loan request, swaps, etc.).
- This means your “secret strategy” is already visible before it even executes.

👉 **Result**: If the opportunity is profitable, a bot can simply copy your logic, submit with a higher gas tip, and front-run your trade.

---
### 3. Execution and Selfdestruct
- When a validator simulates your transaction before adding it to a block, the entire execution path is revealed: borrow → swap → profit → selfdestruct.
- Even though selfdestruct removes the contract’s bytecode after execution, the following are still permanently recorded:
  - Transaction input data (the deployment bytecode + constructor args).
  - Event logs (e.g., Transfer events from tokens).
  - State changes (balances, reserves updated).
  - Full execution trace (visible via tools like Tenderly or Etherscan’s “Trace” tab).

👉 **Result**: Selfdestruct doesn’t erase history — it only deletes the code from the contract’s address after the fact.

---
### 4. After the Block
- Anyone analyzing the blockchain can reconstruct what happened.
- Profit is visible (e.g., your wallet balance increased).
- The contract’s code might be gone, but the deployment bytecode and full transaction trace remain in the blockchain’s immutable history.

👉 This makes ephemeral contracts poor tools for “hiding” strategies.

---
### 5. Can You Hide From MEV Bots?
- **Public mempool**: No. Bots see everything and can front-run you.
- **Private relays (Flashbots Protect, MEV-Share, Eden)**:
  - Your transaction bypasses the public mempool.
  - Only the selected validator sees it before inclusion.
  - This prevents frontrunning, but once mined, the trace is still public.

👉 **You can delay exposure, not prevent it**.

---
### Lessons Learned
- `selfdestruct` only cleans up state after execution; it does not provide privacy.
- Mempool visibility means **any public transaction can be copied or front-run**.
- The only mitigation is using private relays (e.g., Flashbots) to submit trades.
- All execution traces and profit outcomes remain permanently visible on-chain.

---
### References
- [Ephemeral Contract](https://blog.ueex.com/crypto-terms/ephemeral-contract/)
- [Flashbots — Protecting Transactions](https://docs.flashbots.net/)
- [Tenderly Transaction Traces](https://docs.tenderly.co/)
- [Flash Loans](https://www.cyfrin.io/blog/flash-loans-everything-you-need-to-know)
- [Flash Loan Arbitrage](https://www.calibraint.com/blog/building-a-flash-loan-arbitrage-smart-contract)
