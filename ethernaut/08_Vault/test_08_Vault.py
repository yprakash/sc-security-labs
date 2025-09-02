import os

from sc_test_utils import get_web3_instance, load_w3_contract


def test_unlock_vault():
    file_name = os.path.basename(__file__)
    print(f": Setting up the module {file_name}")
    parent_dir = os.path.dirname(os.getcwd())
    challenge_dir = os.path.join(parent_dir, file_name[5:-3])

    w3 = get_web3_instance()
    password = w3.to_bytes(text="A very strong secret password :)")

    vault_contract = load_w3_contract(challenge_dir, constructor_args=[password])
    password = None
    assert vault_contract.functions.locked().call()
    assert password is None
    print("Verified that the deployed Vault contract is locked and used password is reset to None")

    pwd = w3.eth.get_storage_at(vault_contract.address, 1)
    print(f"Retrieved pwd using w3.eth.get_storage_at(1): {pwd.decode()}")
    vault_contract.functions.unlock(pwd).transact({'from': w3.eth.accounts[0]})
    assert not vault_contract.functions.locked().call()
    print("Verified that the Vault contract is unlocked")
