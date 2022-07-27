"""TargetDatabend target sink class, which handles writing streams."""

from __future__ import annotations
import pymysql
from asyncio.log import logger
from typing import Optional, List
from xmlrpc.client import boolean

from singer_sdk.sinks import BatchSink
from target_databend.connector import get_connection


class TargetDatabendSink(BatchSink):
    """TargetDatabend target sink class."""

    max_size = 10000  # Max records to write in one batch

    @property
    def databend_connetion(self) -> pymysql.Connect:
        return get_connection(self.config)

    @property
    def table_name(self) -> str:
        parts = self.stream_name.split("-")
        if len(parts) == 1:
            return self.stream_name
        else:
            return parts[-1]

    @property
    def full_table_name(self) -> str:
        return self.quote(self.get_fully_qualified_name(self.table_name, self.config.get("dbname")))

    @property
    def columns(self) -> List:
        """Get the column names for the table."""
        return [self.quote(key) for key in self.schema["properties"].keys()]

    @staticmethod
    def get_fully_qualified_name(
        table_name: str,
        db_name: Optional[str] = None,
        delimiter: str = ".",
    ) -> str:
        """Concatenates a fully qualified name from the parts.

        Args:
            table_name: The name of the table.
            db_name: The name of the database. Defaults to None.
            delimiter: Generally: '.' for SQL names and '-' for Singer names.

        Raises:
            ValueError: If table_name is not provided or if neither schema_name or
                db_name are provided.

        Returns:
            The fully qualified name as a string.
        """
        if db_name:
            result = delimiter.join([db_name, table_name])
        elif table_name:
            result = table_name
        else:
            raise ValueError(
                "Could not generate fully qualified name for stream: " + ":".join(
                    [
                        db_name or "(unknown-db)",
                        table_name or "(unknown-table-name)",
                    ]
                )
            )

        return result

    def quote(self, name: str) -> str:
        """Quote a name if it needs quoting, using '.' as a name-part delimiter.

        Examples:
          "my_table"           => "`my_table`"
          "my_database.my_table" => "`my_database`.`my_table`"

        Args:
            name: The unquoted name.

        Returns:
            str: The quoted name.
        """
        return ".".join(
            [
                f"`{part}`"
                for part in name.split(".")
            ]
        )

    def table_exists(self, full_table_name: str) -> bool:
        with self.databend_connetion.cursor() as cursor:
            cursor.execute(f"SHOW TABLES LIKE '{full_table_name}'")
            result = cursor.fetchone()
            if result:
                return True
            return False

    def get_column_ddl(self) -> List:
        """
        Get the column DDL for the table.
        Databend does not support PrimaryKey and AutoIncrement.
        """
        properties = self.schema["properties"]
        column_ddl: List = []
        for key, value in properties.items():
            column_jsontype_list: List = value["type"]
            column_is_nullable: boolean = False
            if "null" in column_jsontype_list:
                column_is_nullable = True
            if len(column_jsontype_list) == 1:
                column_jsontype = column_jsontype_list[0]
            else:
                column_jsontype = column_jsontype_list[1]

            column_sqltype: str = ""
            if column_jsontype == "string":
                if value.get("format") == "date-time":
                    column_sqltype = "TIMESTAMP"
                elif value.get("format") == "date":
                    column_sqltype = "DATE"
                else:
                    column_sqltype = "VARCHAR"
            elif column_jsontype == "integer":
                column_sqltype = "INT"
            elif column_jsontype == "number":
                column_sqltype = "DOUBLE"
            elif column_jsontype == "boolean":
                column_sqltype = "BOOLEAN"
            elif column_jsontype == "object":
                column_sqltype = "VARIANT"
            elif column_jsontype == "array":
                column_sqltype = "ARRAY"
            else:
                raise ValueError(f"Unknown column type: {column_jsontype}")

            column_ddl.append(f"{self.quote(key)} {column_sqltype} {'NULL' if column_is_nullable else 'NOT NULL'}")
        return column_ddl

    def create_table(self, full_table_name: str) -> None:
        """Create a table in the database.

        Args:
            full_table_name: The fully qualified name of the table.
        """
        column_ddl: List = self.get_column_ddl()
        create_table_sql: str = f"CREATE TABLE IF NOT EXISTS {full_table_name} ({','.join(column_ddl)})"
        try:
            with self.databend_connetion.cursor() as cursor:
                cursor.execute(create_table_sql)
            self.databend_connetion.commit()
        except Exception as e:
            logger.error(f"Error creating table: {e}, create_table_sql: {create_table_sql}")
            raise e

    def start_batch(self, context: dict) -> None:
        """Start a batch.

        Developers may optionally add additional markers to the `context` dict,
        which is unique to this batch.
        """
        # Sample:
        # ------
        # batch_key = context["batch_id"]
        # context["file_path"] = f"{batch_key}.csv"

    def prepare_table(self) -> None:
        """
        Prepare the table for writing.
        Use this method to create the table if it does not exist.
        """
        self.create_table(self.full_table_name)

    # def process_record(self, record: dict, context: dict) -> None:
    #     """Process the record.

    #     Developers may optionally read or write additional markers within the
    #     passed `context` dict from the current batch.
    #     """
    #     # Sample:
    #     # ------
    #     # with open(context["file_path"], "a") as csvfile:
    #     #     csvfile.write(record)

    def process_batch(self, context: dict) -> None:
        """Write out any prepped records and return once fully written."""
        self.prepare_table()
        records_to_drain = context["records"]
        insert_sql = f"INSERT INTO {self.full_table_name} ({','.join(self.columns)}) VALUES ({','.join(['%s' for _ in self.columns])})"
        records = [list(item.values()) for item in records_to_drain]
        try:
            with self.databend_connetion.cursor() as cursor:
                cursor.executemany(insert_sql, records)
            self.databend_connetion.commit()
        except Exception as e:
            logger.error(f"Error inserting records: {e}, insert_sql: {insert_sql}")
            raise e
