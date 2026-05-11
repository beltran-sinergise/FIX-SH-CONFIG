"""Script to fix legends in SentinelHub configurations."""

import argparse
import logging

from src.SHconfig import ConfigBuilder, read_configuration
from src.utils import update_all_configs, update_config

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
    args = argparser.parse_args()

    sh_config = read_configuration(args.conf)
    lister = ConfigBuilder(sh_config, "", "")

    if args.update_all:
        update_all_configs(lister)
    elif args.update_list:
        for config_id in args.update_list:
            config = lister.get_config(config_id)
            update_config(lister, config)


if __name__ == "__main__":
    main()
