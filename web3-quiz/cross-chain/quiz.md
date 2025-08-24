### EIP-155 and Replay Protection
Which EIP was introduced to mitigate replay attacks across Ethereum and its forks?  
A. EIP-712  
B. EIP-155  
C. EIP-4337  
D. EIP-2612
> B
#### The Problem Before EIP-155
Before 2016, Ethereum transactions only contained the signature `(v, r, s)` without binding to a chain context. After the Ethereum/Ethereum Classic fork, a transaction signed on one chain could be replayed on the other, since both chains shared the same transaction format.
#### The Fix in EIP-155
- EIP-155 added the `chainId` into the signature calculation.
- Specifically, the `v` value in the signature was modified to encode the `chainId`.
- This ensures that the transaction is only valid on the chain for which it was signed.
#### Security Impact
- Transactions from Ethereum cannot be replayed on Ethereum Classic anymore.
- All EVM-compatible chains (Polygon, BSC, Avalanche) adopt chain IDs to avoid cross-chain replay risk.

### Chain Separation in EIP-712
Suppose a dApp uses EIP-712 typed signatures for off-chain approvals. Which element in the signing domain is **critical** to prevent cross-chain replay?  
A. `verifyingContract`  
B. `chainId`  
C. `name`  
D. `salt`
> B
#### EIP-712 Basics
EIP-712 defines structured, human-readable signatures for typed data. It introduces a _domain separator_ so that the same data signed in one context cannot be reused in another.
#### Why `chainId` is Critical
- Including `chainId` ensures that a signature is valid only for the intended blockchain.
- Without it, a signature created on Ethereum Mainnet could be replayed on a fork (Goerli, Polygon, etc.).
#### Role of Other Fields
- `verifyingContract`: Binds the signature to one smart contract, preventing replay across contracts.
- `name` / `version`: Prevent collisions between dApps or protocol versions.
- `salt`: Optional uniqueness, but not standard for chain separation.  
Thus, chainId is the anchor against cross-chain replay in EIP-712.

After EIP-155, why can off-chain signatures (e.g., permit() in ERC20) still be vulnerable to replay on multiple chains if not designed carefully?  
A. Because EIP-155 does not apply to off-chain signatures.  
B. Because nonces are reused across chains.  
C. Because permit() does not require a gas fee.  
D. Because ERC20 approvals are global.
> A
- EIP-155 solves replay attacks for **on-chain transactions** by including `chainId` in the transaction signature.
- But for **off-chain signed messages** (e.g., approvals, meta-transactions, permit-based flows), EIP-155 is irrelevant because these are not raw Ethereum transactions. They are arbitrary pieces of data signed by users.
#### Risk
If the signed data does not explicitly include `chainId` or `verifyingContract`, the same signed message can be replayed on another EVM-compatible chain or even on another contract.

#### Example in ERC20 `permit()`
- User signs an approval message for token spending.
- If the message format lacks `chainId`, an attacker can replay it on multiple chains where the same token contract is deployed.

#### Web3.py Context
- In **web3.py**, when you sign messages (`w3.eth.account.sign_message` or `sign_typed_data`), you must ensure the schema includes chain-specific and contract-specific fields.
- Otherwise, the signature is valid globally across chains.
- That’s why libraries like OpenZeppelin’s `EIP712` base contracts enforce `chainId` and `verifyingContract`.
