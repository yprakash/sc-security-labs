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

def test_gatekeeper1_exploit(setup_module):
    w3, challenge_dir = setup_module
    gatekeeper_contract = load_w3_contract(challenge_dir, file_name="GatekeeperOne.sol", version='0.8.0')
    attacker = w3.eth.accounts[1]
    assert gatekeeper_contract.functions.entrant().call() != attacker  # Initial check
    print('Attacking with the EOA:', attacker)

    attacker_contract = load_w3_contract(challenge_dir, file_name="GatekeeperOneAttacker1.sol", version='0.8.0',
                                         deployer_index=1, constructor_args=[gatekeeper_contract.address])
    attempts, gas_used = attacker_contract.functions.attack().call({'from': attacker})
    print("Attempts:", attempts)
    print("Successful gas:", gas_used)
    # assert gatekeeper_contract.functions.entrant().call() == attacker
    print(f"Tested GatekeeperOne")
