# Challenge 03 - Coin Flip
In contracts like Lottery/gambling, we may need to introduce a certain degree of randomness (feeding of numbers that are not known ahead of time). Generating randomness is generally a difficult computing problem, but especially more difficult in smart contracts. You don't even want to implement random number generator in contracts. But when we want it (Lottery dApp..), we do some sort of randomness through decentralized oracle.

Generating random numbers in solidity can be tricky. There currently isn't a native way to generate them, and everything you use in smart contracts is publicly visible, including the local variables and state variables marked as private. Miners also have control over things like blockhashes, timestamps, and whether to include certain transactions - which allows them to bias these values in their favor.

To get cryptographically proven random numbers, you can use Chainlink VRF, which uses an oracle, the LINK token, and an on-chain contract to verify that the number is truly random.

Some other options include using Bitcoin block headers (verified through BTC Relay), RANDAO, or Oraclize).
