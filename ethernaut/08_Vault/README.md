# Ethernaut Level 08 — Vault

### Challenge
The goal is to unlock the `Vault` contract by setting its `locked` variable to `false`.  
The only way to do this is by providing the correct `password` stored in the contract.

### Vulnerable Logic
```solidity
bool public locked = true;
bytes32 private password;
function unlock(bytes32 _password) public {
    if (password == _password) {
        locked = false;
    }
}
```
### Vulnerability Explained
Although the `password` variable is marked `private`, in Ethereum **all contract storage is publicly accessible** on-chain.  
By reading the appropriate storage slot, anyone can retrieve the supposedly secret `password` and call `unlock()` to bypass the intended protection.

### Key Insights
- `private` in Solidity only restricts access at the language level; it does **not** make data secret on-chain.
- Any contract storage value can be read with `eth_getStorageAt` / `w3.eth.get_storage_at`.
- Security through obscurity (storing secrets on-chain) is ineffective.

### Lessons Learned
- Never store sensitive information (passwords, keys, seeds) directly on-chain.
- Assume all storage data is public, regardless of `private` or `internal` visibility.
- If secrecy is required, use off-chain mechanisms or cryptographic proofs instead.

### References
- [Ethernaut Level 8 — Vault](https://ethernaut.openzeppelin.com/level/0xB7257D8Ba61BD1b3Fb7249DCd9330a023a5F3670)
- [Solidity Docs: Visibility](https://docs.soliditylang.org/en/latest/contracts.html#visibility-and-getters)
- [eth_getStorageAt JSON-RPC](https://ethereum.org/en/developers/docs/apis/json-rpc#eth_getstorageat)
- [web3.eth.get_storage_at](https://web3py.readthedocs.io/en/stable/web3.eth.html#web3.eth.Eth.get_storage_at)
