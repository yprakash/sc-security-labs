# Ethereum JSON-RPC
### What Is JSON-RPC?
Ethereum clients (Geth, Nethermind, Erigon, etc.) expose a [JSON-RPC](https://www.jsonrpc.org/specification) interface.  
This API is the lowest-level bridge between researchers and the chain. It lets you query state, simulate transactions, and even send raw signed transactions.

JSON-RPC gives **direct visibility into storage and execution**, bypassing Solidity abstractions.  
When auditing, this means you can:
- Inspect contract storage (e.g., "private" variables).
- Trace calls, events, and gas usage.
- Replay or simulate attacks against local forked chains.

---
### Core Methods for Security Work
Here are the most useful JSON-RPC calls in a security context:
#### 🔹 `eth_getStorageAt`
Reads the raw 32-byte word at a given storage slot.
```bash
curl -X POST --data '{
  "jsonrpc":"2.0",
  "method":"eth_getStorageAt",
  "params": [
    "0xContractAddressHere",
    "0x0",
    "latest"
  ],
  "id":1
}' -H "Content-Type: application/json" https://mainnet.infura.io/v3/YOUR_API_KEY
```
- `0x0` slot → the storage index, hex, padded to 32 bytes (0 here)
- `latest` block → or a block number

---
#### 🔹 `eth_call`
Executes a call without submitting a transaction (no gas cost, read-only).
```bash
{
  "jsonrpc":"2.0",
  "method":"eth_call",
  "params": [
    {
      "to": "0xContractAddressHere",
      "data": "0x70a08231000000000000000000000000YourAddressHere"
    },
    "latest"
  ],
  "id":1
}
```
**use-case**: simulating how a contract function would behave in the current state.  
Auditors use this to check balances, return values, or whether an input could bypass a modifier.

---
#### 🔹 `eth_sendRawTransaction`
Broadcasts a signed transaction (useful for custom-crafted calldata or replaying exploits).
```bash
{
  "jsonrpc":"2.0",
  "method":"eth_sendRawTransaction",
  "params": ["0xSignedTxDataHere"],
  "id":1
}
```
**use-case**: replaying attack payloads from testnets or simulating transactions against a forked chain.

---
#### 🔹 `debug_traceTransaction` (Client-Specific)
Not part of the Ethereum JSON-RPC spec, but Geth/Nethermind expose it.  
It traces every opcode executed during a transaction.
```bash
{
  "method": "debug_traceTransaction",
  "params": ["0xTxHashHere", {}],
  "id": 1,
  "jsonrpc": "2.0"
}
```
**use-case**: analyzing reentrancy, delegatecall, or gas-griefing behavior at opcode level.

---
### Storage Layout & Security Implications
When inspecting storage with `eth_getStorageAt`, remember Solidity’s layout rules:
- State variables are assigned slots sequentially.
- Smaller types (e.g., `uint8`, `bool`) are packed into the same 32-byte slot.
- Fixed-size arrays occupy consecutive slots.
- Dynamic arrays and mappings use `keccak256(slot + index)` to determine storage location.

#### Practical attack vector:
Protocols that assume `private` protects secrets (keys, random seeds, commit values) are vulnerable, since anyone can read storage with JSON-RPC.

---
### Key Takeaways
- JSON-RPC is the ground truth interface for Ethereum security research.
- `eth_getStorageAt` breaks the illusion of on-chain secrecy.
- `eth_call` and `debug_traceTransaction` are vital for simulating or dissecting attacks.
- Understanding storage layout is essential to map variables to slots.
- Security engineers should master JSON-RPC to move beyond Solidity’s abstractions.

---
### References
- [Ethereum JSON-RPC API](https://ethereum.org/en/developers/docs/apis/json-rpc/)
- [Geth Debug API](https://geth.ethereum.org/docs/interacting-with-geth/rpc/ns-debug)
- [Solidity Storage Layout](https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html)
