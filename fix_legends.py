"""Script to fix legends in SentinelHub configurations."""

import argparse
import logging

from src.SHconfig import ConfigBuilder, read_configuration
from src.utils import update_all_configs, update_config, is_clms_config

logging.basicConfig(level=logging.WARNING, format="%(levelname)s\t%(message)s")
logger = logging.getLogger("src.SHconfig")
logger.setLevel(logging.DEBUG)


def main() -> None:
    """Main function to fix legends in SentinelHub configurations."""
    argparser = argparse.ArgumentParser(
        description="Fix legends in SentinelHub configurations."
    )
    update_group = argparser.add_mutually_exclusive_group(required=True)
    update_group.add_argument(
        "--update-all", action="store_true", help="Update all SH configurations."
    )
    update_group.add_argument(
        "--update-list",
        nargs="+",
        help="Update specific SH configurations from a list.",
    )
    argparser.add_argument(
        "--conf",
        type=str,
        help="Path to the SentinelHub configuration file.",
        default="conf",
    )
    argparser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which layers would be updated without making any changes.",
    )
    argparser.add_argument(
        "--clms-only",
        action="store_true",
        help="Skip Sentinel and Landsat configurations, only process CLMS products.",
    )
    args = argparser.parse_args()

    sh_config, domain_account_id = read_configuration(args.conf)
    lister = ConfigBuilder(sh_config, "", domain_account_id)

    if args.update_all:
        update_all_configs(lister, dry_run=args.dry_run, clms_only=args.clms_only)
    elif args.update_list:
        config_ids = args.update_list
        for config_id in config_ids:
            config = lister.get_config(config_id)
            if args.clms_only and not is_clms_config(config):
                logger.info(
                    f"Skipping non-CLMS config: {config.get('name')} ({config_id})"
                )
                continue
            update_config(lister, config, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
