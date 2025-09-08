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

def test_elevator_exploit(setup_module):
    w3, challenge_dir = setup_module
    elevator = load_w3_contract(challenge_dir, file_name='Elevator.sol', contract_name='Elevator', version='0.8.0')
    top = elevator.functions.top().call()
    assert not top
    print('Checked elevator top', top)

    attacker = load_w3_contract(challenge_dir, file_name='BuildingFloor.sol', contract_name='BuildingFloor', version='0.8.0')
    tx = attacker.functions.attack().transact()
    tx = w3.eth.wait_for_transaction_receipt(tx)
    assert tx.status == 1
    top = elevator.functions.top().call()
    assert top
    print('Checked elevator top', top)
