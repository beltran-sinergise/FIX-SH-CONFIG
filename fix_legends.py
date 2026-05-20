"""Script to fix legends in SentinelHub configurations."""

import argparse
import logging

from src.SHconfig import ConfigBuilder, read_configuration
from src.utils import update_all_configs, update_config, _is_clms_config

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s\t%(message)s"
)
logging.getLogger('src.utils').setLevel(logging.DEBUG)


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
        help="Show what would be updated without making API changes.",
    )
    argparser.add_argument(
        "--clms-only",
        action="store_true",
        help="Only process CLMS products (config name must contain 'CLMS' or 'clms').",
    )
    args = argparser.parse_args()

    sh_config = read_configuration(args.conf)
    lister = ConfigBuilder(sh_config, "", "")

    if args.update_all:
        update_all_configs(lister, dry_run=args.dry_run, clms_only=args.clms_only)
    elif args.update_list:
        config_ids = args.update_list
        if args.clms_only:
            config_ids = [
                config_id for config_id in config_ids
                if _is_clms_config(lister.get_config(config_id)["name"])
            ]
            logging.getLogger("src.utils").info(
                f"CLMS filter: processing {len(config_ids)} of {len(args.update_list)} configs"
            )
        for config_id in config_ids:
            config = lister.get_config(config_id)
            update_config(lister, config, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
