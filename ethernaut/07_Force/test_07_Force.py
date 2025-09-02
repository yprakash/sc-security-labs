import os

import pytest

from sc_test_utils import get_web3_instance, load_w3_contract


@pytest.fixture(scope="module")
def setup_module():
    file_name = os.path.basename(__file__)
    print(f": Setting up the module {file_name}")
    parent_dir = os.path.dirname(os.getcwd())
    challenge_dir = os.path.join(parent_dir, file_name[5:-3])
    w3 = get_web3_instance()
    yield w3, challenge_dir
    print(f"\nTearing down the module: {file_name}")

def test_exploit(setup_module):
    w3, challenge_dir = setup_module
    empty_contract = load_w3_contract(challenge_dir, file_name='Force.sol')
    initial_balance = w3.eth.get_balance(empty_contract.address)
    assert initial_balance == 0
    print("Verified Initial balance of force contract:", initial_balance)

    contract_bal_wei = w3.to_wei(1, 'ether')
    hack_contract = load_w3_contract(challenge_dir, file_name='ForceAttack.sol', value=contract_bal_wei)
    tx_hash = hack_contract.functions.attack(empty_contract.address).transact({'from': w3.eth.accounts[0]})

    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    assert tx_receipt.status == 1
    final_balance = w3.eth.get_balance(empty_contract.address)
    assert final_balance == w3.from_wei(contract_bal_wei, 'wei')
    print("Verified Final balance of empty contract:", final_balance)
