import os

import pytest

from sc_test_utils import get_web3_instance, load_w3_contract

version = '0.6.12'
# NOTE: This is not yet validated because of 0.6.12 version, but logic should be similar.

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
    deployer_index = 0
    depositor_index = 1
    attacker_index = 2
    w3, challenge_dir = setup_module
    target = load_w3_contract(challenge_dir, file_name='Reentrance.sol',
                              version=version, deployer_index=deployer_index)
    deposit_amounts = [w3.to_wei(1, 'ether')]
    attack_amounts = [w3.to_wei(1, 'ether')]

    for deposit in deposit_amounts:
        for amt in attack_amounts:
            tx_hash = target.functions.donate(w3.eth.accounts[depositor_index]).transact({
                'from': w3.eth.accounts[depositor_index], 'value': deposit
            })
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            assert tx_receipt.status == 1
            assert deposit == target.functions.balanceOf(w3.eth.accounts[depositor_index]).call()
            assert deposit == w3.eth.get_balance(target.address)

            hacker = load_w3_contract(challenge_dir, file_name='ReentranceAttack.sol',
                                      version=version, constructor_args=[target.address, amt])
            tx_hash = hacker.functions.transact({'from': w3.eth.accounts[attacker_index]})
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            assert tx_receipt.status == 1
            print(f"Tested for deposit_amount {deposit} and attack_amount {amt}")
