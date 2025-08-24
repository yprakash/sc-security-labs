## Who is a Relayer?
#### Definition
A relayer is any actor (usually a server, bot, or even another user) that **submits an off-chain signed message to the blockchain on behalf of the signer**.
- The user signs data with their private key → does **not** broadcast it.
- The relayer collects the signature and wraps it in a blockchain transaction (using their own ETH/MATIC/etc. to pay gas).
- The smart contract verifies the signature on-chain (using `ecrecover` or EIP-712).

#### In web3.py context
- A relayer is just anyone who calls `w3.eth.send_raw_transaction()` with the signed message included.
- For example, in **meta-transactions** or `permit()` flows, you could write a Python bot that:
  1. Collects signed permits from users.
  2. Packages them into a real Ethereum transaction.
  3. Pays gas itself.
- So **yes**, anyone using web3.py can act as a relayer if they have ETH for gas and know how to encode/submit the signature to the contract.
