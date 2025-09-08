## Ethernaut Level 11 — Elevator

The `Elevator` contract is meant to simulate an elevator system. You must trick it into thinking it's reached the top floor using a malicious `Building` contract.  
In simple terms: Make the elevator contract think it has reached the top floor.

---
### 🔍 Vulnerability
The `Elevator` contract calls the `isLastFloor(uint)` function **twice**:
1. To check if the floor is the last one.
2. Then conditionally calls `goTo()` if the result is `false`.

Since it **does not store the return value** of the first call, if `isLastFloor()` returns different values between the two calls, you can bypass the logic and make `top = true`.

---
### 🔓 Exploit Strategy

1. Deploy a malicious `Building` contract that implements the `isLastFloor(uint)` interface.
2. Inside `isLastFloor(uint)`:
   - Return `false` on the **first call** (allow elevator to go).
   - Return `true` on the **second call** (trick elevator into thinking it’s at the top).
3. Call `elevator.goTo(floor)` via your attack contract.
4. Submit the instance when `elevator.top()` returns `true`.
---
### 💡 Key Takeaways
- Interfaces can be tricked using stateful logic.
- Never call the same external function multiple times without caching the result.
- External calls are untrusted — assume they can behave adversarially.
