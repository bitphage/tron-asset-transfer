import pytest

from tron_asset_transfer.transfer import Transfer, TransferConfig, Wallet


@pytest.fixture()
def config():
    config = TransferConfig(
        contracts={"USDT": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"},
        my_wallets={
            "foo": Wallet(
                privkey="326cb9386e60b5a7bbd435c629394ce275f5e83070500c2f7c3782e8aca113f2",
                pubkey="TKorRmBMJTHmUE1kXAuTHCZnkLQuCfcukq",
            )
        },
        destinations={"alice": "TDqtfgFEgzVZakJMMCNEjKjgkX99CxMuMp"},
    )
    return config


def test_config_creation(config):
    assert config is not None


def test_transfer_usdt(config):

    transfer_helper = Transfer(config)
    txn = transfer_helper.transfer_with_contract(
        source_wallet="foo", asset="USDT", destination="alice", amount=120.45, dry_run=True
    )
    assert txn.to_json() is not None
