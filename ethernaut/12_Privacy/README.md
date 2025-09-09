# Ethernaut Level 12 — Privacy
### Challenge Goal
Unlock the contract by finding the correct `bytes32` key, despite the variable being marked as `private`.

### Vulnerability Essence
The contract stores its secret key in a private state variable, but in Solidity "private" only restricts *contract-level access*, not blockchain visibility.  
Minimal snippet:
```solidity
bytes32[3] private data;
function unlock(bytes16 _key) public {
    if (_key == bytes16(data[2])) {
        locked = false;
    }
}
```
### Explanation
A common misconception is that marking variables as `private` hides them from everyone. In reality, **all Ethereum contract storage is publicly readable on-chain**. Private/public only affects how other Solidity contracts can access the variable — not humans, RPC calls, or tools like `eth_getStorageAt`.

#### Reading Storage Example
You can read the supposed “secret” with a JSON-RPC call:
```bash
curl -X POST --data '{
  "jsonrpc":"2.0",
  "method":"eth_getStorageAt",
  "params": [
    "0xContractAddressHere",
    "0x5", 
    "latest"
  ],
  "id":1
}' -H "Content-Type: application/json" https://mainnet.infura.io/v3/YOUR_API_KEY
```
- 0x5 → the storage slot index for data[2].
- The result is a 32-byte hex string, which can be cast down to `bytes16` to match the contract’s `unlock()` function.

In this challenge, the supposed “secret” unlock key is sitting openly in storage. An attacker doesn’t need to guess; they can read it directly from the blockchain state and use it to call `unlock()`.  
It can also be read using tools like:
- Web3.py or web3.js
- Hardhat/Foundry
- Etherscan's `storageAt`

---
### 🛠️ Exploit Strategy
1. Read storage slot `5` directly (where the key is stored).
2. Truncate it from `bytes32` to `bytes16`.
3. Call the `unlock()` function with the truncated value.

---
### 🧩 Key Takeaways
- private ≠ hidden on-chain
- All contract state can be read via getStorageAt
- Type casting in Solidity follows left-alignment (bytes16(bytes32) takes the first 16 bytes)
