import logging
import random
from typing import Any, Dict, List

import yaml
from pydantic import BaseModel
from tronpy import Contract, Tron
from tronpy.keys import PrivateKey
from tronpy.providers import HTTPProvider

logger = logging.getLogger(__name__)

TRX_PRECISION = 6


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
    nodes: List[str]

    @classmethod
    def from_yaml_file(cls, path):
        with open(path, "r") as fd:
            config = yaml.safe_load(fd)
        return cls.parse_obj(config)


class Transfer:
    def __init__(self, config: TransferConfig):
        self._config = config
        provider = HTTPProvider(random.choice(self._config.nodes))  # noqa: DUO102
        self._client = Tron(provider)

    @staticmethod
    def amount_to_int(amount: float, precision: int) -> int:
        return int(amount * 10**precision)

    @staticmethod
    def amount_to_int_by_contract(amount: float, contract: Contract) -> int:
        """Convert amount to integer value used by contracts."""
        precision = contract.functions.decimals()
        return Transfer.amount_to_int(amount, precision)

    @staticmethod
    def send_transaction(txn: Any, dry_run: bool = False) -> Any:
        if dry_run:
            return txn
        result = txn.broadcast()
        return result.wait()

    def transfer_with_contract(
        self,
        source_wallet: str,
        asset: str,
        destination: str,
        amount: float,
        dry_run: bool = False,
    ) -> Any:
        contract_addr = self._config.contracts[asset]
        contract = self._client.get_contract(contract_addr)
        int_amount = self.amount_to_int_by_contract(amount, contract)
        txn = (
            contract.functions.transfer(self._config.destinations[destination], int_amount)
            .with_owner(self._config.my_wallets[source_wallet].pubkey)
            .fee_limit(100_000_000)
            .build()
            .sign(PrivateKey(bytes.fromhex(self._config.my_wallets[source_wallet].privkey)))
        )
        return self.send_transaction(txn, dry_run)

    def transfer_trx(
        self,
        source_wallet: str,
        destination: str,
        amount: float,
        dry_run: bool = False,
    ) -> Any:
        int_amount = self.amount_to_int(amount, TRX_PRECISION)
        txn = (
            self._client.trx.transfer(
                from_=self._config.my_wallets[source_wallet].pubkey,
                to=self._config.destinations[destination],
                amount=int_amount,
            )
            .build()
            .sign(PrivateKey(bytes.fromhex(self._config.my_wallets[source_wallet].privkey)))
        )
        return self.send_transaction(txn, dry_run)
