# Meta-Transaction Relayers
### Overview
A **meta-transaction** is a transaction that a user wants to execute, but instead of sending it directly (and paying gas), they sign a message off-chain.  
A **relayer** (third party) then submits this signed message on-chain, paying the gas on behalf of the user.

This pattern is common in **gasless apps (dApps)**, onboarding flows, and UX-friendly wallets.

---
### How It Works
1. User signs a message describing the intended function call.  
   - Example: “I want to `transfer(10 tokens to Bob)`”.  
   - Signed with their private key, but not broadcast.
2. The signed message is sent to a **relayer server**.
3. The relayer bundles it into a blockchain transaction and pays gas.
4. The smart contract verifies the user’s signature, then executes the action as if the user had sent it.  

---
### Minimal Example
```solidity
function executeMetaTx(
    address user,
    bytes memory functionData,
    bytes memory signature
) public {
    require(verify(user, functionData, signature), "Invalid signature");
    (bool success, ) = address(this).call(functionData);
    require(success, "Meta-tx failed");
}
```
- The relayer calls `executeMetaTx`.
- The contract ensures the `user` signed it.
- The function executes with `user` as the logical sender.

---
### Why Useful
- Users don’t need ETH for gas (good for onboarding).
- Better UX in games, DeFi, and NFTs.
- Allows **sponsored transactions** (project pays gas).

---
### Security Considerations
- **Replay Protection:** Prevent the same signed message from being reused multiple times. Solution: include and track a nonce per user.  
- **Nonce Management:** Each user needs their own incrementing nonce to ensure every meta-tx is unique.  
- **Relayer Trust:** Relayers could censor or delay transactions. Use trusted forwarders (EIP-2771) or multiple relayers.  
- **Gas Griefing:** Users could make relayers waste gas by submitting failing transactions. Relayers often require a fee or trust arrangement.

---
### Real-World Uses
- EIP-2771: Trusted Forwarders
- GSN (Gas Station Network).
- Many dApps’ “Sign in with MetaMask” + “Gasless Tx” flows.

---
### Key Takeaways
- Meta-transactions shift **gas costs** from users to relayers.
- Contracts must carefully handle **signature verification + replay protection**.
- Widely used for **onboarding non-crypto users** into dApps.

---
### References
- [EIP-2771: Secure Protocol for Gasless Transactions](https://eips.ethereum.org/EIPS/eip-2771)
- [Gas Station Network](https://opengsn.org/)
