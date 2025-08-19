## Fee-on-Transfer Tokens
Most ERC20 tokens behave predictably: if Alice transfers 100 tokens, Bob receives 100 tokens.  
But Fee-on-Transfer tokens introduce a twist: a transaction fee is automatically deducted on transfer.

**Example**:
- Alice sends `100` tokens to Bob.
- The token contract deducts `5%` as a fee.
- Bob receives only `95`. The `5` tokens are burned or sent to a treasury/reward pool.

👉 **Security Implication**:
- Smart contracts assuming `transfer()` sends the full amount (e.g., DEX liquidity pools, lending protocols), will break ([SWC-132](https://swcregistry.io/docs/SWC-132/)).
- Attackers can exploit this mismatch to cause accounting errors, drain liquidity, or manipulate reserves.
