# Contract Type Referencing in Solidity

## Overview
In Solidity, a contract can hold references to other contracts of the **same type** (or even itself).  
This is not the same as embedding objects in Java/Python — instead, Solidity treats every contract reference as an **address** with type safety.

### Example: SocialNetwork Contract

```solidity
pragma solidity ^0.8.20;

contract SocialNetwork {
    SocialNetwork public friend;

    function setFriend(SocialNetwork _friend) external {
        friend = _friend;
    }
    function poke() external {
        friend.poke();  // Calls the friend contract
    }
}
```
### How it works
- `SocialNetwork` is both a **type** and a contract.
- The variable `friend` is internally just an `address`, but restricted to point only to contracts of type `SocialNetwork`.
- Initially, `friend` = `address(0)`.
- After deployment, you can link one `SocialNetwork` contract to another:
```solidity
SocialNetwork alice = new SocialNetwork();
SocialNetwork bob = new SocialNetwork();

alice.setFriend(bob);   // Alice’s contract knows Bob
bob.setFriend(alice);   // Bob’s contract knows Alice
// You can even self-reference:
alice.setFriend(alice); // Alice points to herself
```
---
### Comparison with Java/Python

In Java/Python, a class can hold a reference to its own type:
```python
class Node:
    def __init__(self):
        self.peer: "Node" = None
```
In Solidity:
- `friend` is not an object but the **address of a deployed contract**.
- Solidity contracts are immutable once deployed; linking happens via storage assignments.
---
### Why this matters
- **Design patterns**: Useful for peer-to-peer, cooperative contracts, or linking proxy contracts.
- **Security**: If a contract points to a malicious peer, function calls like `friend.doSomething()` may execute attacker logic. Always validate external references.
---
## ❌ DeFi Attack Use Cases
### 1. Cross-Contract Reentrancy

If `poke()` were instead a function like `withdraw()` or `claimRewards()`, the attacker could link two malicious peers that bounce calls back and forth, draining funds before state is updated.
- Attacker sets `friend` to a malicious contract that reenters.
- When the victim calls `friend.withdraw()`, attacker re-calls `withdraw()` before balances are updated.
- This is a **cross-contract version of TheDAO hack**.

### 2. Reserve Drain via Mid-Transaction Manipulation

Suppose a lending protocol references a `ReserveManager` contract of the same type.  
If governance allows `setReservePeer()`, an attacker can:
- Replace the peer with a malicious Reserve contract.
- During a borrow/repay flow, the system queries the malicious peer for balances.
- Attacker returns inflated/forged balances → bypassing collateral checks and draining reserves.

### 3. Governance Bait-and-Switch

In DAO-style systems, peers may vote or delegate to each other:
- Contract `DAO1` sets `DAO2` as a peer.
- Attacker upgrades `DAO2` to a malicious implementation (via proxy or upgradeable beacon).
- Now, any peer calls (`peer.castVote()`, `peer.delegate()`) execute malicious logic.

Result: attacker hijacks governance or redirects votes.

### 4. Infinite Loop Denial-of-Service

If peers are not carefully validated, setting two contracts as friends can lead to infinite recursion:
```solidity
alice.setFriend(bob);
bob.setFriend(alice);
alice.poke(); // gas exhausted → DoS
```
A simple logic bug becomes a resource exhaustion vector in production.

---
## 🔒 Security Takeaways
- Always **validate peer contracts** before linking (`onlyOwner`, `isTrusted`, `address.code.length > 0`).
- Use **reentrancy guards** and **checks-effects-interactions** even across peers.
- For DAOs and DeFi, avoid direct peer calls for balance/accounting logic → use immutable snapshots or Merkle proofs.
- Treat cross-referencing as **governance/architecture-level risk**, not just low-level Solidity risk.
---

## Key Point

Self-referential contract types look like OOP patterns, but in DeFi they create **attack graphs** where multiple contracts can be tricked into calling each other, enabling reentrancy, reserve manipulation, or governance capture.
