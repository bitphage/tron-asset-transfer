#!/usr/bin/env python
import click

from tron_asset_transfer.transfer import Transfer, TransferConfig


@click.group()
def main():
    pass


@main.command()
@click.argument("source")
@click.argument("destination")
@click.argument("amount")
@click.argument("asset")
@click.option("--config", default="config.yaml")
@click.option("--dry-run", is_flag=True)
def transfer(source, destination, amount, asset, config, dry_run):
    """
    Transfer some AMOUNT of ASSET.

    SOURCE must be a key in `my_wallets`

    DESTINATION must be a key in `destinations`

    AMOUNT is a regular amount like 10.55 (assume USDT) - will be automatically converted to proper integer value

    ASSET is asset like USDT, USDC etc, but should have a mapping in `contracts`
    """
    parsed_config = TransferConfig.from_yaml_file(config)
    transfer_helper = Transfer(parsed_config)
    result = transfer_helper.transfer_with_contract(
        source_wallet=source, asset=asset, destination=destination, amount=float(amount), dry_run=dry_run
    )
    click.echo(result)


if __name__ == "__main__":
    main()
