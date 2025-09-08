# Mutex (Mutual Exclusion)
### 🔹 Overview
A **mutex** (mutual exclusion object) is a synchronization mechanism used in operating systems, multithreaded programming, and smart contracts. Its purpose is simple:  
👉 Ensure that only one execution thread can access a shared resource at a time.
- In OS/Software: Prevents race conditions when multiple threads/processes try to access shared memory or files.
- In Solidity/EVM: Prevents reentrancy attacks when multiple contract calls try to modify state concurrently.

---
### 🔹 Mutex in Operating Systems
- Imagine two threads writing to the same variable in memory:
  - Without mutex: `x = x + 1` can overlap → corrupt state.
  - With mutex: Thread 1 locks, updates `x`, unlocks → then Thread 2 proceeds safely.

#### Example (pseudocode)
```c
mutex lock;
void increment() {
    lock(mutex);
    shared_counter++;
    unlock(mutex);
}
```
✅ Prevents race conditions.  
❌ If a thread forgets to release lock → deadlock.

### 🔹 Mutex in Solidity
Ethereum is **single-threaded**, but contracts can call each other recursively (via `call`, `delegatecall`, or reentrancy).  
A **mutex flag** ensures that once a function starts executing, no recursive entry can re-enter it until it finishes.

Example
```solidity
contract MutexExample {
    bool private locked;
    modifier noReentrant() {
        require(!locked, "Reentrancy blocked");
        locked = true;
        _;
        locked = false;
    }
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }
    function withdraw(uint256 amount) external noReentrant {
        require(balances[msg.sender] >= amount, "Not enough balance");
        balances[msg.sender] -= amount;
        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent, "ETH transfer failed");
    }
}
```
### 🔑 Key Takeaways
- OS world: Mutex prevents race conditions in concurrent programs.
- Solidity world: Mutex prevents reentrancy by blocking nested calls.
- Both work on the same principle → **lock before entering, unlock when leaving**.
- Widely adopted in Solidity via OpenZeppelin’s `ReentrancyGuard`.
