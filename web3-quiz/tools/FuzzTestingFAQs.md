### FAQs on Fuzz Testing and Invariants

Why are invariants useful in fuzz testing?
> They specify conditions that must always hold true, helping detect subtle violations.
---

Consider the invariant:
```solidity
assert(totalSupply == balances[alice] + balances[bob]);
```
During fuzz testing, this assertion fails. What does this most likely indicate?
> There is a potential bug that causes the accounting of balances to drift from `totalSupply`.
- If invariant breaks, it’s a logic/accounting bug, not a “fuzzing glitch”.
---

A common misconception about fuzzing in Solidity is:  
A. It can find edge cases that developers might not anticipate.  
B. It can fully prove the absence of bugs in the contract.  
C. It works well in combination with invariants for stronger assurance.  
D. It can be integrated with tools like Foundry or Echidna.
> It can fully prove the absence of bugs in the contract.
---

What is a key limitation of fuzz testing?
> It provides probabilistic confidence, not absolute guarantees.
---

Which scenario is fuzz testing **least effective** at detecting?  
A. Reentrancy in low-level calls.  
B. Invariant violations in accounting logic.  
C. Rare bugs that require highly specific sequences of transactions.  
D. Integer overflow in simple arithmetic.
> C: Rare, sequence-dependent bugs are hard for fuzzing → you need stateful/advanced fuzzing.
---

In Echidna (a popular fuzzing tool), how are invariants typically defined?  
A. As functions prefixed with test_ returning bool.  
B. As public functions returning bool with no arguments.  
C. As events that emit when conditions break.  
D. As modifiers attached to functions under test.
> B: In Echidna, invariants = _public bool-returning funcs, no args_.
---

Which statement about fuzz testing with Foundry (`forge`) is correct?  
A. Foundry fuzzing guarantees full path coverage.  
B. Foundry can automatically generate random inputs for property-based tests.  
C. Foundry fuzzing only works for ERC-20 contracts.  
D. Foundry fuzzing requires manual seed input for every run.
> B: Foundry = property-based fuzzing, auto input generation.
---

Why combine fuzz testing with invariant checking?  
A. Invariants make fuzzing deterministic.  
B. Fuzzing explores random inputs, invariants specify what must never break.  
C. Invariants eliminate all false positives.  
D. Fuzz testing alone is sufficient, so invariants are optional decoration.
> B: Perfect — fuzzing = search space, invariants = safety rules. Together → strong combo.
---

What is a false positive in the context of fuzz testing?

A. The fuzzing tool reports a bug that does not exist in reality.
B. The tool misses a real bug due to limited randomness.
C. An invariant check passes even though the contract is unsafe.
D. The fuzzer repeats the same input multiple times.
> A: False positive = tool claims bug, but reality → no bug (not just in fuzzing).
---

Which of the following is a **strength** of fuzz testing in Solidity contracts?
> Can reveal unexpected edge cases developers didn’t anticipate.
---

Suppose you define an invariant like below. What kind of bug would this most likely catch?
```solidity
function invariant_totalSupply() public view returns (bool) {
    return totalSupply == balances[alice] + balances[bob];
}
```
A. Arithmetic overflow in multiplications.  
B. Missing balance update in transfer logic.  
C. Incorrect gas calculation in loops.  
D. Reentrancy in fallback functions.
> B: Missing balance update in transfer logic.
---

If fuzzing keeps repeating the same small set of inputs, what is a possible cause?  
A. The fuzzer is broken.  
B. The input domain is constrained (e.g., `require(x < 10)`).  
C. Solidity does not allow larger numbers.  
D. The invariant is incorrectly defined.
> The input domain is constrained → fuzzer can’t explore beyond defined limits.
---

Which of the following best describes differential fuzzing?
> Comparing outputs of two contract implementations for the same random inputs.
- **Differential fuzzing** involves testing two or more implementations of the same functionality against the same inputs, then comparing the outputs to identify discrepancies.
- Instead of checking “is my contract safe?”, it checks:
  > “Do two different implementations behave the same way under the same random inputs?”
- Examples:
  - Compare your ERC-20 implementation vs OpenZeppelin’s.
  - Feed both the same random transfers/mints/burns.
  - If at any point balances diverge → you’ve found a bug.
- Benefit:
  - Catch logic deviations you wouldn’t notice with only one contract.
- Limitation:
  - Only as strong as your “trusted reference implementation”.  
---

What is the main challenge with fuzz testing DeFi contracts?  
A. They have no external dependencies.  
B. State space is extremely large due to composability.  
C. Random inputs cannot affect balances.  
D. DeFi contracts are usually too simple for fuzzing to add value.  
> State space is extremely large due to composability.

- **Composability**: the ability to combine smaller, independent modules or components to create larger systems or solutions.
- Composability (**DeFi Context**): contracts can interact with each other _like Lego bricks_.
- **Example**: A lending protocol (Compound) gives you cDAI, which you can use in another protocol (Uniswap) to provide liquidity, which in turn gives LP tokens you stake elsewhere.
- **Why fuzzing gets harder**:
  - Each additional contract adds more **state space** (possible combinations of balances, approvals, collateral ratios).
  - A fuzzer might randomly create a call order that breaks assumptions (e.g., withdraw from one protocol while another still relies on the locked funds).
- Note: Composability makes fuzzing useful but very challenging → because of exponential state explosion.
---
