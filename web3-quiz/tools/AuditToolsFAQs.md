### Static analysis false positive
A static analyzer flags this function as **potentially vulnerable to reentrancy**. Why is this **most likely a false positive**?
```solidity
mapping(address => uint256) public balances;
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount, "Insufficient balance");

    // Update state **before** external call
    balances[msg.sender] -= amount;

    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```
> The analyzer is using **pattern matching**; it cannot detect that balances are updated **before** the external call.
- The key here is **state update ordering**: `balances[msg.sender] -= amount;` happens **before** the external call.
- Static analyzers like Slither detect `call` patterns and may flag functions where an external call occurs **after any state interaction**, even if the state has already been updated safely.
- This is a classic false positive: the code is **actually safe from reentrancy**, but the analyzer cannot reason about execution order precisely in all contexts.

---

Why would you use a dynamic analysis tool like Echidna or Forge fuzzing after static analysis?  
> To simulate real execution flows and detect edge cases missed by static analysis.
- Dynamic analysis tools **execute the contract**, simulating transactions and state changes across many inputs.
- They catch runtime issues, edge cases, and state-dependent vulnerabilities that static analysis cannot detect.
- Examples:
  - Complex economic logic that depends on multiple contract interactions.
  - Reentrancy that only triggers under specific conditions.
  - Invariant violations that occur after multiple sequential calls.
- **Key point**: Dynamic analysis complements static analysis, but does not replace manual reasoning — you still need to interpret results, design invariants, and validate findings.

---

You are using Echidna to test an ERC20 token. You define an invariant like below. During fuzzing, Echidna reports a violation. What is the **most likely reason**?
```solidity
invariant totalSupplyInvariant() public view returns (bool) {
    return totalSupply() == sumOfAllBalances();
}
```
> There is an **edge case in your contract logic** causing totalSupply to diverge from balances.
- The report indicates that **some sequence of calls or edge-case inputs** caused `totalSupply()` to no longer equal the sum of all balances — a real logic violation.
- Fuzzers like **Echidna** detect these by repeatedly generating random inputs and checking user-defined properties.

### FYI
- Solidity **does NOT have** an `invariant` keyword natively. This is **Echidna-specific syntax** (or in other fuzzers, you write “property functions”):
  - Echidna treats functions that return bool and are public/view as invariants to test.
  - For example:
```solidity
function echidna_totalSupplyInvariant() public view returns (bool) {
    return totalSupply() == sumOfAllBalances();
}
```
- The `echidna_` prefix is conventional so Echidna automatically detects it.

---

While fuzzing a contract, you notice Echidna reports invariant violations, but manual review shows **no realistic scenario can break the invariant**. What is the **most likely cause**?
> The invariant function itself contains a **bug or incorrect calculation**.
- Dynamic analysis tools like Echidna report violations based on your defined invariants.
- If the invariant function itself has a bug (e.g., miscalculates `sumOfAllBalances()`), the fuzzer will report a violation **even though the contract logic is correct**.
- This is a **fuzzer “false positive”** — not the same as static analysis false positives, but similar in concept: the **tool can only be as correct as the properties you define**.

---

Why can dynamic analysis with fuzzing (e.g., Echidna) miss critical bugs even if no invariant fails during tests?
> Because fuzzing cannot generate enough random inputs to cover every possible execution path.
- Fuzzers like Echidna test contracts by generating lots of random/semi-random inputs.
- But the input space is **huge** → practically impossible to cover all paths.
- If your invariants are sound, and no failure is triggered, it **doesn’t mean the contract is safe** — it just means the fuzzer hasn’t hit the right combo yet.

---

Which of the following is the biggest practical limitation of combining static + dynamic analysis in smart contract auditing?
> They cannot detect logic flaws or economic vulnerabilities that don’t show up in code patterns.
- Static + dynamic tools **complement each other** (pattern scanning + real execution).
- But neither can reason about business logic flaws or economic vulnerabilities — e.g., governance exploits, flawed incentive designs, or sandwich attack vectors. These **require human reasoning**.
