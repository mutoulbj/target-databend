"""TargetDatabend target class."""

from __future__ import annotations

from singer_sdk.target_base import Target
from singer_sdk import typing as th

from target_databend.sinks import (
    TargetDatabendSink,
)


class TargetDatabend(Target):
    """Target for TargetDatabend."""

    name = "target-databend"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "host",
            th.StringType,
            default="localhost",
            required=True,
            description="The hostname of the databend.",
        ),
        th.Property(
            "port",
            th.IntegerType,
            default="3307",
            required=True,
            description="The port of the databend.",
        ),
        th.Property(
            "user",
            th.StringType,
            required=True,
            description="The username of the databend.",
        ),
        th.Property(
            "password",
            th.StringType,
            required=True,
            description="The password of the databend.",
        ),
        th.Property(
            "dbname",
            th.StringType,
            required=True,
            description="The database name of the databend.",
        )
    ).to_dict()

    default_sink_class = TargetDatabendSink
