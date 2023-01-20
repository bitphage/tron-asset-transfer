import logging
from typing import Any, Dict

import tronpy
import yaml
from pydantic import BaseModel
from tronpy import Tron
from tronpy.keys import PrivateKey

logger = logging.getLogger(__name__)


class Wallet(BaseModel):
    # HEX-encoded privkey
    privkey: str
    pubkey: str


class TransferConfig(BaseModel):
    # Map contract name to its address, e.g. USDT -> xxx
    contracts: Dict[str, str]
    # Support multiple own wallets, e.g. main, mobile, etc
    my_wallets: Dict[str, Wallet]
    # Aliases for destinations
    destinations: Dict[str, str]

    @classmethod
    def from_yaml_file(cls, path):
        with open(path, "r") as fd:
            config = yaml.safe_load(fd)
        return cls.parse_obj(config)


class Transfer:
    def __init__(self, config: TransferConfig):
        self._config = config
        self._client = Tron()

    @staticmethod
    def amount_to_int(amount: float, contract: tronpy.Contract) -> int:
        """Convert amount to integer value used by contracts."""
        precision = contract.functions.decimals()
        return int(amount * 10 ** precision)

    def transfer_with_contract(
        self, source_wallet: str, asset: str, destination: str, amount: float, dry_run: bool = False,
    ) -> Any:
        contract_addr = self._config.contracts[asset]
        contract = self._client.get_contract(contract_addr)
        int_amount = self.amount_to_int(amount, contract)
        txn = (
            contract.functions.transfer(self._config.destinations[destination], int_amount)
            .with_owner(self._config.my_wallets[source_wallet].pubkey)
            .fee_limit(100_000_000)
            .build()
            .sign(PrivateKey(bytes.fromhex(self._config.my_wallets[source_wallet].privkey)))
        )
        if dry_run:
            return txn
        result = txn.broadcast()
        return result.wait()
