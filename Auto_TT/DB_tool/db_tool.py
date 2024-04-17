import os.path
import re
import pymysql
import json


class myDB:
    def __init__(self, db_name):
        with open(os.path.dirname(__file__) + os.sep + "config.json", "r") as json_file:
            db_settings = json.load(json_file)
            db_settings["db"] = db_name
        self.db = pymysql.connect(**db_settings)

    def select_data(self, table_name: str, column_list: list, where_clause=""):
        """
        Get the data in given table and return
        Args:
            table_name: the table name to fetch data
            column_list: the column list to get data
            where_clause: the condition to filter data

        Returns: the search result

        """
        column_list_str = ",".join(column_list)
        select_command = f"SELECT {column_list_str} from {table_name} {where_clause}"
        print(select_command)
        with self.db.cursor() as cursor:
            cursor.execute(select_command)
            return cursor.fetchall()

    def insert_data(self, table_name: str, column_list: list, data_list: list):
        """
        Insert data to the table
        Args:
            table_name: the table name to fetch data
            column_list: the columns for those data
            data_list: the data to insert
        """
        column_list_str = ",".join(column_list)
        data_list_str = re.sub(r"[\[\]]", "", str(data_list))
        insert_command = f"INSERT INTO {table_name}" \
                         f"({column_list_str}) " \
                         f"VALUES({data_list_str})"
        print(insert_command)
        with self.db.cursor() as cursor:
            cursor.execute(insert_command)
        self.db.commit()

    def update_data(self, table_name: str, update_values: dict, where_clause: str):
        """
        update the specific data with the input data
        Args:
            table_name: the table name to fetch data
            update_values : the specific columns and data to update
            where_clause: to filter which data to be updated
        """
        update_values_str = ", ".join(
            [f"{column}={data}" for column, data in update_values.items()]
        )
        update_command = f"UPDATE {table_name} SET {update_values_str} {where_clause}"
        print(update_command)
        with self.db.cursor() as cursor:
            cursor.execute(update_command)
        self.db.commit()

    def delete_data(self, table_name: str, where_clause=""):
        """
        Delete the rows by the condition
        Args:
            table_name: the table name to fetch data
            where_clause: to filter which data rows to be deleted
        """
        delete_command = f"DELETE FROM {table_name} {where_clause} "
        print(delete_command)
        with self.db.cursor() as cursor:
            cursor.execute(
                delete_command)
        self.db.commit()


if __name__ == '__main__':
    db = myDB("monkey_test")
    table_name = "test_table"
    # db.delete_data(table_name, "where id=7")
    # db.update_data(table_name,"text_field","2","WHERE id = 5")
    # print(db.select_data(table_name, ["*"]))
