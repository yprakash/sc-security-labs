# Transaction Ordering and MEV

Ethereum transactions are not executed in the order users submit them. Instead, validators choose which transactions to include in a block and in what sequence. This freedom of ordering creates both opportunities and risks — most notably, **Maximal Extractable Value (MEV).**

Many real-world exploits do not come from a single buggy line of code, but from how multiple transactions interact when ordered differently in the mempool or in a block.

---
### 1. Deterministic Execution vs. Ordering Freedom

- Inside the **EVM**, transaction execution is **deterministic and atomic**.  
- Once a transaction begins, it runs to completion (or reverts) with no interleaving of other transactions.  
- However, across transactions in a block, validators (or block builders) can reorder, insert, or exclude transactions.  

👉 This freedom at the block level is where ordering-dependent vulnerabilities arise.

---
### 2. Where Ordering Risks Appear
#### Front-running
- An attacker sees a pending profitable transaction in the mempool.  
- They copy it, set a higher gas tip, and get included first.  
- Example: Sniping an arbitrage or NFT mint before the original sender.

#### Back-running
- An attacker submits a transaction to execute **immediately after** a target transaction.  
- Example: Capturing arbitrage opportunities created by a large swap.

#### Sandwich Attacks
- The attacker places **one transaction before and one after** a victim’s swap.  
- The first tx moves the price unfavorably for the victim; the second tx reverts it back, capturing profit.  

#### Liquidation Races
- Multiple bots compete to liquidate undercollateralized positions.  
- The winner depends entirely on transaction ordering and gas bidding.

---
### 3. Why This Matters for Auditors
- **Not about concurrency:**  
  Ethereum is single-threaded — no two transactions run in parallel inside the EVM.  
  The danger comes from *ordering*, not parallel execution.
- **State assumptions may break:**  
  If a contract assumes “my tx will execute next,” an attacker may reorder things to invalidate that assumption.
- **Examples in audits:**  
  - Unprotected DEX arbitrage mechanisms.
  - Lending protocols without anti-sandwich protections.
  - Auctions where bidders can be front-run.

---
### 4. Mitigation Patterns
- **Commit–Reveal Schemes**  
  Users first commit to an action (hashed), then reveal later, preventing frontrunners from copying inputs.
- **Batch Auctions**  
  Grouping trades into a batch and settling at a uniform clearing price eliminates ordering advantage.
- **MEV-Aware Infrastructure**  
  Submitting transactions via private relays (e.g., Flashbots Protect) hides them from the public mempool.  

---
### Lessons Learned
- The EVM runs transactions **sequentially and deterministically**, but block-level ordering is adversarial.  
- MEV exploits stem from this **freedom of ordering**, not from code-level concurrency.  
- As auditors, it’s critical to identify contract logic that can be abused by **transaction ordering manipulation**.  
- Secure design often requires cryptographic commitments, batching, or off-chain coordination.  

---
### References
- [Ethereum.org — Transactions](https://ethereum.org/en/developers/docs/transactions/)
- [Flashbots — Introduction to MEV](https://docs.flashbots.net/)
- [Chainsecurity — Transaction Ordering Dependence](https://chainsecurity.com/transaction-ordering-dependence/)
