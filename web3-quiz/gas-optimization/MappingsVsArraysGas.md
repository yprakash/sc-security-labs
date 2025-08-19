### Mappings vs arrays — gas efficiency and safety
You need to store and frequently check whether an address is in a whitelist. Which choice is generally **most gas-efficient for lookups**?

A. `address[] whitelist;` with linear search  
B. `mapping(address => bool) whitelist;`  
C. `address[] whitelist;` sorted and binary search  
D. Both A and B have same lookup gas  

- `mapping(address => bool)` lookups are **O(1)** and cost just a single `SLOAD` (~2,100 gas first read, ~100 gas after).
- `address[]` + linear search is **O(n)**, costing gas proportional to the array size — and in worst cases, can exceed the block gas limit, causing a **DoS risk** for large lists.
- Sorted arrays + binary search still **require multiple storage reads** and added computation.

**Security angle**:  
Using arrays for membership checks in production has caused exploitable DoS vulnerabilities in DAOs and NFT whitelists — once the list grows too big, it becomes impossible to process in a single transaction.