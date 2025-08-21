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
