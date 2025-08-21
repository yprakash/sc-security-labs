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

---
