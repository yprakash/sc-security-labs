### Function modifiers & gas
Which change is more gas-efficient in Solidity ≥0.8.0?

A. Using function modifiers instead of `require` statements in each function  
B. Using `require` inline instead of modifiers  
C. Both are equal in cost  
D. Modifiers are cheaper only if they’re `pure`  

Answer: B. inline `require`  
- **Modifiers** in Solidity are essentially syntactic sugar — the compiler inlines the modifier code into each function where it’s used.
- If a modifier contains only a `require`, inlining it into multiple functions **repeats the same code multiple times**, increasing bytecode size.
- Larger bytecode can slightly increase **deployment cost** and may also affect **runtime gas** if the modifier has additional jumps or duplicated code segments.
- Writing the `require` directly inside the function body can be marginally cheaper in gas and avoids bytecode bloat.

**Security angle**:  
Modifiers are still valuable for **readability** and enforcing cross-cutting concerns like access control, but in gas-critical loops or frequently called functions, inline checks can save costs.  
In security audits, we sometimes recommend **removing low-value modifiers** to both reduce gas and bytecode attack surface.
