"""Utility functions for fixing and managing SentinelHub configuration legends.

This module provides functions to convert color formats, update legend styles,
and manage SentinelHub configurations with focus on legend color validation.
"""

import logging
import pprint
import re
from typing import Any
import requests
from src.SHconfig import ConfigBuilder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def new_color(color: str) -> str:
    """Convert color format to RGB percentage format.

    Args:
        color: Input color string containing numeric values.

    Returns:
        RGB color string in percentage format (e.g., "rgb(50%,75%,100%)").
    """
    orig = re.findall(r"(\d+(\.\d+)*)", color)
    numbers = [round(float(match[0])) for match in orig]
    return "rgb({}%,{}%,{}%)".format(*numbers)


def fix_color_list(color_list: list[dict[str, str]]) -> list[dict[str, str]]:
    """Fix color format in a list of color dictionaries.

    Args:
        color_list: List of dictionaries containing color information.

    Returns:
        List with updated color formats converted to RGB percentages.
    """
    return [dict(item, color=new_color(item["color"])) for item in color_list]


def new_styles(styles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Update styles by fixing gradient colors in legends.

    Args:
        styles: List of style dictionaries containing legend information.

    Returns:
        Updated styles with fixed gradient colors.
    """
    new_styles_list = []
    for style in styles:
        if "gradients" in style["legend"]:
            gradients = fix_color_list(style["legend"]["gradients"])
            new_styles_list.append(
                {**style, "legend": {**style["legend"], "gradients": gradients}}
            )
        else:
            new_styles_list.append(style)
    return new_styles_list


def update_config(lister: ConfigBuilder, config: dict[str, Any]) -> None:
    """Update configuration by fixing colors in all layers.

    Args:
        lister: ConfigBuilder instance for managing configurations.
        config: Configuration dictionary containing the config ID.
    """
    layers = lister.get_layers(config["id"])
    for layer in layers:
        logger.info(
            f"Testing layer {layer['id']} in config {config['id']} before update."
        )
        test_parse_response(config["id"], layer["id"])

        new_layer = layer
        if "gradients" in new_layer["styles"][0]["legend"]:
            new_layer["styles"][0]["legend"]["gradients"] = fix_color_list(
                new_layer["styles"][0]["legend"]["gradients"]
            )
        if "items" in new_layer["styles"][0]["legend"]:
            new_layer["styles"][0]["legend"]["items"] = fix_color_list(
                new_layer["styles"][0]["legend"]["items"]
            )

        logger.info(f"Updating layer {layer['id']} in config {config['id']}...")
        lister.set_layer(config["id"], layer["id"], new_layer)
        logger.info(
            f"Testing layer {layer['id']} in config {config['id']} after update."
        )
        test_parse_response(config["id"], layer["id"])
        logger.info("------------------------------------")


def update_all_configs(lister: ConfigBuilder) -> None:
    """Update all configurations by fixing legend colors.

    Args:
        lister: ConfigBuilder instance for managing configurations.
    """
    configs = lister.list_configs()
    for config in configs:
        update_config(lister, config)


def test_layer(config_id: str, layer_id: str) -> requests.Response:
    """Test a layer by making a GetLegendGraphic WMS request.

    Args:
        config_id: Configuration ID.
        layer_id: Layer ID to test.

    Returns:
        HTTP response from the WMS request.
    """
    return requests.get(
        f"https://sh.dataspace.copernicus.eu/ogc/wms/{config_id}?service=WMS&request=GetLegendGraphic&layer={layer_id}"
    )


def list_error_legends(lister: ConfigBuilder) -> None:
    """List all layers that have legend errors.

    Iterates through all configurations and tests each layer's legend.
    Prints error information for layers that return non-200 status codes.

    Args:
        lister: ConfigBuilder instance for accessing configurations.
    """
    configs = lister.list_configs()
    for config in configs:
        layers = lister.get_layers(config["id"])
        for layer in layers:
            response = test_layer(config["id"], layer["id"])
            if response.status_code != 200:
                logger.error("-----")
                logger.error(
                    f"Error for config {config['name']} with ID {config['id']}, layer {layer['id']}"
                )
                logger.error(response.url)


def get_error_legends(lister: ConfigBuilder) -> list[dict[str, Any]]:
    """Get all configurations that have legend errors."""
    configs = lister.list_configs()
    configs_with_errors = []
    for config in configs:
        layers = lister.get_layers(config["id"])
        for layer in layers:
            response = test_layer(config["id"], layer["id"])
            if response.status_code != 200:
                configs_with_errors.append(config)

    return configs_with_errors


def remove_first_element_of_gradient(layer: dict[str, Any]) -> dict[str, Any]:
    """Remove the first element from a layer's gradient list.

    Args:
        layer: Layer dictionary containing styles and legend information.

    Returns:
        Updated layer with the first gradient element removed.
    """
    gradients = layer["styles"][0]["legend"]["gradients"]
    new_gradients = gradients[1:]
    new_layer = layer
    new_layer["styles"][0]["legend"]["gradients"] = new_gradients
    return new_layer


def fix_first_element(lister: ConfigBuilder, config_id: str, layer_id: str) -> None:
    """Fix a layer by removing the first gradient element.

    Args:
        lister: ConfigBuilder instance for accessing configurations.
        config_id: Configuration ID.
        layer_id: Layer ID to fix.
    """
    layers = lister.get_layers(config_id)
    layer = next(iter(layers))
    new_layer = remove_first_element_of_gradient(layer)
    lister.set_layer(config_id, layer_id, new_layer)


def fix_items(lister: ConfigBuilder, config_id: str, layer_id: str) -> None:
    """Fix legend items by updating their color format.

    Args:
        lister: ConfigBuilder instance for accessing configurations.
        config_id: Configuration ID.
        layer_id: Layer ID whose legend items need to be fixed.
    """
    layers = lister.get_layers(config_id)
    layer = next(layer for layer in layers if layer["id"] == layer_id)
    items = layer["styles"][0]["legend"]["items"]
    new_items = [{**item, "color": new_color(item["color"])} for item in items]
    new_layer = layer
    new_layer["styles"][0]["legend"]["items"] = new_items
    lister.set_layer(config_id, layer_id, new_layer)


def check(lister: ConfigBuilder, config_id: str, layer_id: str) -> None:
    """Check and pretty print a layer's legend configuration.

    Args:
        lister: ConfigBuilder instance for accessing configurations.
        config_id: Configuration ID.
        layer_id: Layer ID to check.
    """
    layers = lister.get_layers(config_id)
    layer = next(layer for layer in layers if layer["id"] == layer_id)
    pprint.pp(layer["styles"][0]["legend"], width=200)


def test(config_id: str, layer_id: str) -> None:
    """Test a layer and pretty print the response.

    Args:
        config_id: Configuration ID.
        layer_id: Layer ID to test.
    """
    r = test_layer(config_id, layer_id)
    pprint.pp(r)


def test_parse_response(config_id: str, layer_id: str) -> None:
    """Test a layer and parse the response.

    Args:
        config_id: Configuration ID.
        layer_id: Layer ID to test.
    """
    r = test_layer(config_id, layer_id)
    if r.status_code == 200:
        logger.info(f"Layer {layer_id} in config {config_id} is in correct format.")
        logger.info(f"Response status: {r.status_code}")
    else:
        logger.error(f"Error for layer {layer_id} in config {config_id}.")
        logger.error(f"Response status: {r.status_code}")
