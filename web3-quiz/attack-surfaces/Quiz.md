### Reentrancy subtlety
Consider this simplified staking contract:
```solidity
contract Staking {
    IERC20 public immutable token;
    mapping(address => uint256) public balance;
    constructor(IERC20 _token) {
        token = _token;
    }
    function deposit(uint256 amount) external {
        require(token.transferFrom(msg.sender, address(this), amount));
        balance[msg.sender] += amount;
    }
    function withdraw(uint256 amount) external {
        require(balance[msg.sender] >= amount, "Not enough");
        balance[msg.sender] -= amount;
        require(token.transfer(msg.sender, amount));
    }
}
```
The token follows ERC20 but is actually an ERC777-compatible token.  
The withdraw function looks CEI-compliant (update state before external call).  
Is this contract reentrancy-safe against a malicious ERC777 token?

A. Yes, CEI is used; balance updated before external call, so safe  
B. No, attacker can reenter deposit during ERC777 tokensReceived hook and inflate balance  
C. No, attacker can reenter withdraw during ERC777 tokensReceived hook and drain funds  
D. Yes, because ERC20 transfer never triggers callbacks
> B. No, attacker can reenter deposit during ERC777 tokensReceived hook and inflate balance
- External call (`transferFrom`) happens **before** state update.
- If token is ERC777, the attacker’s `tokensReceived` hook fires during the transfer.
- Inside the hook, the attacker can call `deposit` again → since `balance[msg.sender]` hasn’t been updated yet, they can recursively cause inconsistent state or bypass accounting.  
That’s a classic reentrancy via deposit.

Why not C?
- C is incorrect because the `withdraw` function updates the balance before the external call, which is CEI-compliant.

**Note**: The trick is **reentrancy inside an external call isn’t always about “taking” immediately** — it’s about creating _unexpected intermediate states_.

Two attack vectors here:
1. Bypassing accounting assumptions:
   - Imagine `deposit()` triggers _another downstream function_ (like emitting an event, minting LP shares, or updating a reward distribution contract) **after** the balance update.
   - If attacker reenters during the `transferFrom`, they could slip in inconsistent states, e.g. mint LP tokens twice before the balance is finalized.
2. Phantom deposits:
   - If `transferFrom` is overridden (malicious ERC777), attacker can lie: return `true` without actually transferring tokens, then reenter to inflate balance.
   - Since balance isn’t updated yet, the system can get out of sync.

So: attacker doesn’t “lose money” — they create **state desync / phantom credit** situations.  
That’s why auditors flag CEI violations in both deposit and withdraw paths.

### 🔎 ERC777 hooks and which calls trigger them?
- `token.transferFrom()`: Yes, this triggers the ERC777 `tokensToSend` (from sender) and `tokensReceived` (to receiver) hooks.
- `token.transfer()`: Also triggers ERC777 hooks the same way.

So in both `deposit()` and `withdraw()` of your contract, the ERC777 `tokensReceived` can fire and give attacker reentrancy entry points.

The **difference** was the ordering of state updates:
- In `deposit()`: state updated after external call → unsafe.
- In `withdraw()`: state updated before external call → safe against balance-inflating reentrancy.

But note: `withdraw()` is still externally calling an `untrusted token contract`, so while balance is safe, the function can still be griefed (e.g., revert in hook → DoS).

---
### External calls & gas griefing
A DEX router calls `token.transferFrom()` in a loop to pull multiple tokens.
If one token reverts with `OutOfGas` (due to ERC777 hook consuming all gas), how does this affect the attack surface?

A. Only that token’s transfer fails, others unaffected  
B. Entire batch reverts — attacker can grief all users by forcing DoS on one transfer  
C. Just consumes extra gas but transaction still succeeds  
D. No effect, ERC20 standard forbids out-of-gas reverts
> B. If one `transferFrom` fails in a loop, the entire transaction reverts.

That means a malicious ERC777 token can DoS the whole batch. Classic griefing attack surface:
- Scenario: Router pulls `DAI`, `USDC`, `MALICIOUS`.
- Malicious token’s `tokensReceived` hook uses all gas or reverts.
- Whole batch fails → no user can swap via router.

This is why Uniswap v2/v3 avoid token batch pulls and enforce isolated calls.

---
### MEV — Sandwich risk
A DEX contract exposes `swapExactTokensForTokens` with no slippage parameter. Users just specify `amountIn` and get `amountOut` at current pool price.  
Question: What’s the primary MEV attack surface here?

A. Front-running user swaps to block them  
B. Sandwiching: attacker inserts buy before, sell after, extracting profit  
C. Time-based arbitrage on oracles  
D. Flash loan reentrancy in the swap
> B. Sandwiching

If a swap function lacks a slippage parameter, users are at the **mercy of MEV bots**:
- Bot sees Alice’s swap in mempool (`10k DAI → ETH`).
- Bot front-runs with a buy (pushing ETH price up).
- Alice’s trade executes at worse rate (slippage not protected).
- Bot back-runs with a sell to capture the spread.

That’s textbook sandwich attack surface.

---
### Privilege escalation subtlety
A contract has:
```solidity
address public admin;
function upgrade(address newImpl) external {
    require(msg.sender == admin, "not admin");
    _upgradeTo(newImpl);
}
```
Initially, `admin` is set to the deployer in the constructor.  
Later, a governance mechanism calls `admin = timelock` (a smart contract).

**Question**: What’s the attack surface now?  
A. None, timelock is trusted  
B. If timelock has upgrade paths (e.g., new governance logic), attacker could seize admin rights through timelock exploitation  
C. Only denial of service, no escalation possible  
D. It’s equivalent to a multisig, so safe
> B

When `admin` is an **EOA**, privilege boundaries are simple.  
But once governance or a timelock contract takes over:
- That contract itself becomes part of the **trusted computing base**.
- If the timelock can be exploited (logic bug, misconfigured delay, compromised proposer/queue logic),
an attacker can **indirectly escalate** into the `upgrade()` function.

So the **attack surface expands**: instead of “only admin key compromised,”  
now **any weakness in governance = proxy hijack**.

This is a recurring real-world issue:
- Compound v2 governance bug (2020).
- Bad Timelock configurations in smaller DAOs.

---
### External call ordering
Look at this payout function:
```solidity
function payWinner(address winner, uint amount) external onlyGame {
    require(balance >= amount, "not enough balance");
    (bool ok,) = winner.call{value: amount}("");
    require(ok, "send failed");
    balance -= amount;
}
```
What’s the attack surface here?  
A. Safe — it updates balance after sending, no issue  
B. Reentrancy risk: state update happens after external call  
C. Denial of service: malicious winner can force send failed  
D. Both B and C
> D. Both B and C
- External call to `winner.call{value: amount}("")` happens **before** balance deduction.
- If `winner` is a contract with a `receive()` or `fallback()`, it can reenter `payWinner()` or other vulnerable functions and exploit the inflated balance.
- Classic CEI violation.
- Even if `winner` isn’t malicious, it could accidentally or intentionally **revert in its fallback**.
- Because `require(ok)` enforces success, payout fails, blocking further progress.
- That’s a griefing surface — attacker doesn’t need to steal funds, just lock them.  
So both risks coexist.
#### Note:
- **The reentrancy vector depends on what** `onlyGame` **actually enforces**.
  - If `onlyGame = require(msg.sender == game)`, then indeed the winner’s fallback **cannot directly reenter** `payWinner()`, since fallback’s `msg.sender` is the contract itself, not the `game`.
  - That blocks _direct recursive_ `payWinner()` calls.

But:
- The attacker’s fallback could instead call **back into the** `game` contract, if the game exposes any entrypoints that eventually call `payWinner()` again.
- So the surface is still there — whether it’s exploitable depends on how `onlyGame` is implemented and whether the call graph loops back.

Additionally, even if reentrancy is blocked here, the **DoS griefing** (C) is still valid: winner can revert → payout fails → funds locked.

👉 So the safer phrasing:
- Always flag CEI violation (balance updated after external call).
- Severity might be lower (Medium) if reentrancy blocked by access control, but still worth reporting because “DoS griefing” + “potential indirect reentrancy via game” are real risks.

---
### MEV & price oracle
A lending protocol uses a TWAP (time-weighted average price) oracle from Uniswap V2.  
Update function:
```solidity
function updatePrice() external {
    (uint112 reserve0, uint112 reserve1,) = pair.getReserves();
    price = reserve1 * 1e18 / reserve0;
}
```
What’s the MEV/attack surface here?  
A. Safe — TWAP prevents manipulation  
B. Vulnerable — this isn’t a TWAP, it’s just a spot price, manipulable with flash loans  
C. Vulnerable only if attacker owns >50% liquidity  
D. No risk — Uniswap is decentralized
> B

That oracle is **not a TWAP at all** — it’s a spot price.
- Anyone with a flash loan can manipulate reserves for 1 block.
- Call `updatePrice()` in that block → oracle updates to fake value.
- Attackers then borrow/lend/trigger liquidations unfairly.

This was exactly what happened in the **bZx / Cheese Bank exploits** (2020).

---
### Oracle design flaw
A contract uses Chainlink price feed:
```solidity
function getPrice() public view returns (int256) {
    return priceFeed.latestAnswer();
}
```
What’s the main security concern here?  
A. None, Chainlink is always safe  
B. Relying on latestAnswer() without staleness check (may return outdated or 0 value)  
C. Vulnerable to sandwich attack  
D. Oracle manipulation with flash loans
> B. Relying on `latestAnswer()` without staleness check
- Relying on `latestAnswer()` is unsafe without checking if the oracle is **stale or invalid**.
You need to use Chainlink’s `latestRoundData()` and check `updatedAt` and round completeness.

---
### Governance attack surface
A DeFi protocol uses governance tokens to vote. Attackers borrow governance tokens via a flash loan and pass a malicious proposal.  
What’s the best defense?

A. Use snapshot of balances at block proposal was created  
B. Require proposal deposits (stake that can be slashed)  
C. Time delay before execution  
D. All of the above
> D. All of the above
- Each mitigation covers a different dimension of the flash-loan governance problem:
1. Snapshotting balances (A) → prevents attackers from voting with flash-loaned tokens since voting power is measured at block proposal creation, not at execution.
2. Proposal deposits / stake (B) → raises the economic cost of spamming malicious proposals. If they fail or are malicious, the stake can be slashed.
3. Timelock delay (C) → even if an attacker sneaks a proposal through, it can’t execute immediately. This gives the community and multisigs time to intervene.

Modern governance frameworks (Compound’s Governor, OpenZeppelin Governor) typically use all three together.

---
### MEV twist
A lending contract lets users liquidate unhealthy positions:
```solidity
function liquidate(address borrower) external {
    require(_isUnhealthy(borrower), "Not liquidatable");
    uint reward = _calcReward(borrower);
    collateral[borrower] -= reward;
    collateral[msg.sender] += reward;
}
```
What’s the **main attack surface** here?  
A. Reentrancy via collateral updates  
B. MEV front-running to steal liquidations  
C. Integer overflow in collateral[borrower] -= reward  
D. Privilege escalation via borrower impersonation
> B. MEV front-running to steal liquidations
- The function `liquidate()` is **permissionless** — anyone can call it.
- That means if you spot a liquidation opportunity and try to call it, a bot can see your transaction
  in the mempool and **front-run** you with a higher gas fee, executing the liquidation first.
- The attacker (MEV bot) earns the liquidation reward instead of you.

This is exactly why protocols like **Aave** and **Compound** suffer heavy MEV competition for liquidations — bots monitor the mempool and race to capture these rewards.

Notable details:
- A: Reentrancy not possible here since no external calls.
- C: Overflow is unlikely in Solidity ≥0.8 (checked arithmetic).
- D: No borrower impersonation risk — the borrower is passed as an address, and health check ensures correctness.

#### 📌 Defense ideas:
- Allow liquidators to submit **sealed bids (commit-reveal)** to reduce MEV.
- Use **flashbots/private transactions** to avoid front-running.
- Implement **auction-style liquidations** (e.g., Dutch auction instead of first-come).

---

A governance contract executes arbitrary proposals:
```solidity
function execute(address target, bytes calldata data) external {
    require(votes[msg.sender] > quorum, "Not enough votes");
    (bool ok, ) = target.call(data);
    require(ok, "Exec failed");
}
```
What’s the **biggest attack surface** here?  
A. Reentrancy via governance calls  
B. Privilege escalation via forged votes  
C. Arbitrary external call execution (function selector abuse)  
D. MEV frontrunning to reorder proposal execution
> C. Arbitrary external call execution (function selector abuse)
- The contract allows **any voted account** to execute arbitrary calldata on any target contract.
- That means if an attacker accumulates enough votes (or exploits governance token manipulation), they can:
  - Call `selfdestruct` on a vault contract.
  - Call `transferOwnership()` on sensitive contracts.
  - Drain treasuries or upgrade proxies.
- This is a **privilege escalation** vector at the **function-call granularity**: the attacker doesn’t need a bug in the target — they just need governance power.

Details on the distractors:
- A: Reentrancy isn’t relevant unless governance executes contracts with external reentry hooks.
- B: Forged votes are another angle but **not the primary danger** in the code given.
- D: MEV frontrunning could reorder execution, but the **bigger systemic risk is arbitrary execution power**.

#### 📌 Real-world reference:
- Compound governance bug (2020): arbitrary function selector allowed malicious proposals to seize admin rights.
- bZx hack (2021): governance takeover led to protocol draining.

---

Which of the following is the most **subtle attack surface** auditors often miss in Solidity contracts?  
A. Incorrect visibility (public vs internal)  
B. Gas griefing (forcing tx failures via out-of-gas)  
C. Unchecked ERC20 return values  
D. Misconfigured access in upgradeable proxy patterns
> D. Misconfigured access in upgradeable proxy patterns
- Upgradeable contracts (UUPS, Transparent, Beacon) delegate critical logic to proxy + implementation patterns.
- If the `upgradeTo()` or `initialize()` functions are not properly **restricted**, an attacker can:
  - Take control of the implementation slot,
  - Deploy a malicious implementation,
  - Or re-initialize the contract with themselves as the admin.
- Unlike simple reentrancy or unchecked ERC20 issues, this is **architecture-level** and often overlooked by both developers and inexperienced auditors.

#### Examples:
- Audius exploit (July 2022): attacker re-initialized proxy, became owner, drained ~$6M.
- ParaSpace exploit attempt (2023): privilege escalation through misconfigured upgradeability.
