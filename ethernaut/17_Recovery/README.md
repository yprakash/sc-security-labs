## 🛡️ Ethernaut Level 17. Recovery: Reverse-engineering a destroyed contract and reclaiming lost funds by leveraging EVM internals

In this level, we are given a contract called Recovery which can create simple token contracts via create(). One such token contract was deployed and ETH was sent to it, but its address was forgotten. The goal is to recover the lost funds by figuring out the contract address and self-destructing it, sending its balance to our address.

---
### 🔍 Technical Takeaways
- EVM Contract Address Derivation
- RLP Encoding
- Keccak256 Hashing
- Raw Transaction Crafting
- No ABI / Contract Object Usage
---
### 🔨 Strategy
1. Find the address of the SimpleToken contract that was created from the Recovery contract using the formula.
2. Prepare calldata for the destroy(address) function manually (no ABI).
3. Send a raw transaction to invoke destroy() with your EOA as the recipient.
4. Validate that your account received the ETH.

---
### 🧠 Understanding the Exploit
1. Finding Contract Address: Smart contract addresses are [computed deterministically](https://docs.soliditylang.org/en/v0.8.30/introduction-to-smart-contracts.html#accounts)
- Manual Method: Take Ethernaut deployed contract address and search its hashes in etherscan.
- Use a tool like **RLP Decoder** or ethers.js CLI to compute keccak256(rlp.encode([deployer, nonce])).
- Python (generic) method:
```python
import rlp
from eth_utils import keccak, to_checksum_address

sender = bytes.fromhex("...")  # deployer address
nonce = b"\x01"
encoded = rlp.encode([sender, nonce])
contract_address = keccak(encoded)[12:].hex()
print("0x" + contract_address)
```
- What I used (without extra `import rlp`, works only for nonce < 128):
```python
rlp_encoded = b'\xd6\x94' + bytes.fromhex(_address[2:]) + b'\x01'
lost_contract_address = keccak(rlp_encoded)[12:]
lost_contract_address = w3.to_checksum_address(lost_contract_address.hex())
```
2. What is RLP?:  
Recursive Length Prefix encoding is used to encode structured data into bytes. Ethereum uses it for serializing transactions and computing contract addresses.
3. Why 0xd6 and 0x94?  
These are not magic numbers, but part of RLP (Recursive Length Prefix) encoding, which Ethereum uses to encode data like [sender, nonce] before hashing it with keccak256.

| Byte   | Meaning                     | Why It's Used                              |
| ------ | --------------------------- | ------------------------------------------ |
| `0x94` | "Next 20 bytes is a string" | 20-byte address (the deployer’s address)   |
| `0xd6` | "List of total 22 bytes"    | The full encoded list `[address, nonce=1]` |

4. **Manual Transaction & Calldata Preparation**  
We need to encode the function call manually (without requiring ABI)
```python
function_selector = w3.keccak(text="destroy(address)")[:4]
args = encode(["address"], [PLAYER_ADDRESS])
data = function_selector + args
```
Then build and send the transaction.

---
### 💡 Real-World Relevance
- This level simulates an actual rescue operation where funds are stuck in a contract whose address is forgotten.
- Understanding RLP and `keccak256` is critical for building tooling around contract analysis and recovery.
- Knowing how to craft `calldata` manually is essential when ABI is unavailable or incomplete.
