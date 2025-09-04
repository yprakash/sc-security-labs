# ⛽ Gas Station Network (GSN)
### 📌 What is GSN?
GSN is a decentralized system that allows users to interact with Ethereum dApps **without needing ETH for gas fees**.

Instead of paying gas directly, a **relayer** covers the transaction cost and gets reimbursed in ERC20 tokens or another mechanism defined by the dApp.

This improves **user onboarding**: newcomers don’t need ETH in their wallet to try a dApp.

---
### 🎯 Core Idea
1. **User signs a meta-transaction** (e.g., “swap tokens”, “vote”, “mint NFT”).
2. **Relayer submits** that transaction on-chain, paying the gas in ETH.
3. **dApp reimburses relayer** in tokens, or the relayer is subsidized by the project.

✅ The user’s transaction executes **as if they had sent it themselves**.

---
### 🛠 Components of GSN
- **Paymaster** → Contract that defines who pays for gas. It can whitelist users or actions.
- **Forwarder** → Contract that verifies signatures and nonces (ensures replay protection).
- **Relayer** → Off-chain service that actually submits transactions to Ethereum.
- **Recipient Contract** → The dApp that ultimately receives and executes the call.

---
### 📖 Example Flow
1. Alice has no ETH but wants to vote on a DAO.
2. She signs a meta-transaction: vote(ProposalID=5).
3. The relayer submits it on-chain, paying gas.
4. The Paymaster reimburses the relayer in DAI.
5. The DAO contract executes the vote as if Alice had directly called it.

---
### 🔐 Security Considerations
- **Replay Attacks** → Prevented using per-user nonces.
- **Relayer** Abuse → Relayer could censor or drop transactions. Mitigated by multiple relayers.
- **Griefing** → Users could submit failing transactions to waste relayer gas. Paymasters should validate meta-txs before sponsoring them.
- **Trust Model** → Applications must carefully design Paymasters; a naive Paymaster can be drained by attackers.

---
### 🧩 Minimal Solidity Example
```solidity
// Simplified Paymaster pattern
contract SimplePaymaster {
    mapping(address => uint256) public nonces;
    function verifyAndPay(address user, bytes calldata sig, bytes calldata callData) external {
        bytes32 hash = keccak256(abi.encode(user, callData, nonces[user]));
        require(recoverSigner(hash, sig) == user, "Invalid signature");
        nonces[user]++; // prevent replay
        // pay relayer back in ERC20
        ERC20(token).transfer(msg.sender, fee);
    }
}
```
---
### 🚀 Why It Matters
- **User onboarding**: no ETH required.
- **Better UX**: users pay fees in stablecoins or don’t see gas at all.
- **Adoption**: GSN is widely used by wallets, DeFi dApps, and NFT platforms.

---
### 🔑 Key Tricks
- Meta-transactions rely heavily on **EIP-712 typed signatures** for security.
- GSN v2 uses a **modular Paymaster** to control which calls are subsidized.
- Attackers might try to exploit a Paymaster that blindly reimburses everything → always validate callData.
