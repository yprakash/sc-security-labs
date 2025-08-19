## Manual Vulnerability Discovery — critical thinking beyond automated scans.

Consider this simplified rewards contract:
```solidity
function distribute(uint256 reward, address[] calldata users) external onlyOwner {
    uint256 share = reward / users.length;
    for (uint256 i = 0; i < users.length; i++) {
        balances[users[i]] += share;
    }
}
```
The code compiles fine under Solidity ^0.8.0. What’s the **manual discovery risk** here?

A. Nothing — Solidity 0.8 auto-reverts on overflow.  
B. Division rounding → leftover dust can accumulate in contract balance, potentially trapped.  
C. users.length can be zero, causing division by zero revert.  
D. Gas griefing if users.length is large.

> C: Division by zero revert.
- The line `uint256 share = reward / users.length;` will **revert with division by zero** if `users.length == 0`.
- This is something **static analyzers might miss** if they don’t check calldata assumptions.
- The owner could accidentally (or maliciously) call with an empty array, bricking reward distribution.

**Other points**:
- **B (rounding dust)** is also a minor concern, but not the main vulnerability — the real bug is the **unchecked zero-array edge case**.
- **D (gas griefing)** is possible if the array is huge, but that’s more of a DoS design issue than a “hidden vulnerability.”

---

### Malicious Token Integration
A lending protocol integrates arbitrary ERC20s:
```solidity
function deposit(address token, uint256 amount) external {
    IERC20(token).transferFrom(msg.sender, address(this), amount);
    balances[msg.sender][token] += amount;
}
```
What’s the (manual discovery) risk here?  
A. If token is a fee-on-transfer token, accounting will break.  
B. Reentrancy attack is possible if token is ERC777.  
C. A malicious token can fake transferFrom success without actually transferring.  
D. All of the above.

> D: All of the above.

This snippet has multiple subtle risks that an automated scan might miss:
1. Fee-on-transfer tokens
   - If a token deducts fees, the actual amount received by the contract < `amount`.
   - The system’s `balances` will be inflated compared to real reserves.
   - → Insolvency risk.
2. ERC777 / malicious ERC20
   - Tokens with hooks (`tokensReceived`) can reenter during `transferFrom`.
   - If another function depends on balances, this can trigger **cross-function reentrancy**.
3. Non-standard ERC20s
   - Some tokens (e.g., USDT) **don’t revert on failure** — they return `false` instead.
   - Without a return check, this code assumes success even if the transfer failed.
   - A malicious token could **return true without moving funds**, inflating balances infinitely.

👉 Together, these make “arbitrary ERC20 support” a high-risk design choice unless handled carefully.

Best practices:
- Use `SafeERC20` from OpenZeppelin (checks return values).
- Handle fee-on-transfer tokens explicitly.
- Add reentrancy guards around deposits.
- Consider token whitelisting.

---

Here’s a governance contract snippet. What’s the manual discovery bug?
```solidity
mapping(address => uint256) public votes;
address public leader;
function vote() external {
    votes[msg.sender] += 1;
    if (votes[msg.sender] > votes[leader]) {
        leader = msg.sender;
    }
}
```
A. Nothing wrong — this is a simple leader election.  
B. leader starts as the zero address, which can never be dethroned if no one votes.  
C. Users can repeatedly call vote() with no cost, inflating votes infinitely.  
D. The contract lacks a require that voters must have tokens.
> C. Users can repeatedly call vote() with no cost, inflating votes infinitely.

- The `vote()` function lets anyone increment their vote count infinitely, since there’s no stake, cost, or constraint.
- This makes the system meaningless — the first spammer wins leader status.
- It’s not a compiler/runtime bug, but a **logic-level flaw** only visible through manual reasoning.

Other options:
- B: Not correct — `leader` being the **zero address at the start isn’t an issue**, because the first voter will automatically replace it.
- D: True in principle (no token-gating), but the core exploitability is infinite free votes.

**Takeaway**: Governance/voting code must always ensure:
- Sybil resistance (one-user-one-vote is never free).
- Clear eligibility checks (based on token balances, NFT ownership, etc.).

---

### Manual Discovery — Auction Logic
What’s the vulnerability that manual review should catch in this NFT auction contract snippet?
```solidity
address public highestBidder;
uint256 public highestBid;
function bid() external payable {
    require(msg.value > highestBid, "Bid too low");
    highestBidder = msg.sender;
    highestBid = msg.value;
}
```
A. Previous bidders never get their ETH refunded.
B. Reentrancy attack on bid.
C. Gas griefing due to repeated bidders.
D. Auction can be front-run by miners.
> A. Previous bidders never get their ETH refunded.
- Each new bid overwrites `highestBid` and `highestBidder`.
- But the contract never refunds the previous highest bidder.
- This means anyone who loses the auction **loses their ETH permanently** — effectively a protocol rug.

👉 This is a manual discovery logic flaw.
- Automated tools rarely flag this, since it’s not an overflow, reentrancy, or missing access control.
- It takes auditor reasoning: “_Wait — where does the old bidder’s ETH go?_”

**Best practice**:  
- Either automatically refund the old bidder:
```solidity
payable(highestBidder).transfer(highestBid);
```
- Or use a **withdraw pattern** where losing bidders can reclaim their ETH later.

Real-world tie-in:
- Many early Ethereum auction contracts had exactly this bug.
- The withdrawal pattern is now considered **safer than auto-refund** (avoid reentrancy risks).
