# Solidity Built-in Functions & Globals – Security Cheat Sheet

Smart contracts have access to a range of built-in variables and functions that expose **EVM state**, **block metadata**, and **gas context**.  
For devs/auditors, these are critical to review because misuse often leads to exploits.

---
## 🔹 Gas & Execution
- `gasleft()` → Remaining gas.  
  ⚠️ Brittle if used in conditions.  
- `selfbalance()` → **internal opcode**, directly returns the contract’s ETH balance.  
  ✅ Safer than `address(this).balance` (esp, in reentrancy-sensitive contexts). gas-efficient, no external call.  

---
## 🔹 Block Context
- `block.timestamp` → Current block’s timestamp, UNIX epoch time in seconds (UTC).  
  ⚠️ Miners can manipulate within ~15 seconds; unsafe for randomness.  
- `block.number` → Current block number.  
  ✅ Reliable for sequencing, but not time.  
- `blockhash(uint blockNumber)` → Hash of recent 256 blocks.  
  ⚠️ Unreliable as randomness source; only works for past blocks.  
- `block.coinbase` → Miner’s(PoW) / Validator’s(PoS) address, receiving the block rewards.  
  ⚠️ Miners can influence rewards if used in logic.  
- `block.gaslimit` → Block gas limit.  
- `block.basefee` → Base fee of current block ([EIP-1559](https://eips.ethereum.org/EIPS/eip-1559)).  
  ⚠️ minimum fee required (burned, not a tip)

---
## 🔹 Transaction Context
- `tx.origin` → Original external account that started the call chain.  
  ⚠️ Insecure for auth ([SWC-115](https://swcregistry.io/docs/SWC-115)).  
- `tx.gasprice` (or `maxPriorityFeePerGas` in EIP-1559) → what you pay to **prioritize** your transaction.  
  ✅ Use priority fee (`maxPriorityFeePerGas`), not block.basefee, for faster inclusion.  
  ⚠️ Not reliable for randomness or security conditions.  

---
## 🔹 Message Context
- `msg.sender` → Immediate caller (EOA or contract).  
- `msg.value` → ETH sent with the call.  

---
## 🔹 Address & Code Introspection
- `address.balance` → ETH balance of an address.  
- `extcodesize(address)` → Size of code at address.  
  ⚠️ Used in some anti-contract checks, but fails with contracts in construction or destroyed.  
- `extcodehash(address)` → Hash of contract code at an address. detect if an address hosts a contract, is an EOA, or is empty.
  - `0x0` → account doesn’t exist.
  - `0xc5d246...` (hash of empty code) → EOA or self-destructed contract.
  - Anything else → deployed contract code hash.
- `extcodecopy(address, ...)` → Copies raw bytecode of another contract into memory.  
  Use-case: **low-level contract inspection** (e.g., clone factories verifying deployed code, contracts validating libraries).  
  ⚠️ Rare in DeFi logic, but relevant in metaprogramming, bytecode validation, or proxies.

---
## 🔹 Cryptographic Primitives
- `keccak256(bytes memory)` → Hash function.  
- `sha256(bytes memory)` → Returns a 32-byte SHA-256 hash of the input.  
- `ripemd160(bytes memory)` → Returns a 20-byte RIPEMD-160 hash of the input.  
- `ecrecover(bytes32 hash, uint8 v, bytes32 r, bytes32 s)` → Recovers address from signature.  
  ⚠️ Must validate inputs; malleability issues in older patterns.  
- `addmod(uint x, uint y, uint k)` → Modular addition.  
- `mulmod(uint x, uint y, uint k)` → Modular multiplication.  

---
## 🔹 Inline Assembly (Yul) Specials
Available in low-level assembly (powerful but dangerous):
- `codesize`
- `gas`
- `balance`
- `caller`
- `callvalue`
- `calldataload`
- `calldatasize`
- `calldatacopy`
- `returndatasize`
- `returndatacopy`

---
## Key Takeaways
- **Randomness:** Never use `block.timestamp`, `blockhash`, or `gasleft()` as randomness sources.  
- **Authentication:** Never use `tx.origin` for authorization.  
- **Contract Detection:** `extcodesize` and friends are unreliable for detecting EOAs.  
- **Gas Tricks:** Gas-based conditions (`gasleft()`, stipends) are brittle and break across forks/EIPs.  
- **Safe Use:** Stick to `msg.sender`, `msg.value`, and cryptographic primitives for reliable logic.  

---
## References
- [Solidity Docs – Special Variables and Functions](https://docs.soliditylang.org/en/latest/units-and-global-variables.html)  
- [SWC Registry](https://swcregistry.io/) – Common smart contract weaknesses  
- [Ethereum Yellow Paper](https://ethereum.github.io/yellowpaper/paper.pdf) – Formal definition of opcodes and execution  
