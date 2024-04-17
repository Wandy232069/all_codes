from itertools import chain
import json
import os
from ldap3 import *
from ldap3.core.exceptions import LDAPBindError

from DB_tool.db_tool import myDB


class LDAPAuthenticator:
    def __init__(self):
        with open(
                os.path.dirname(__file__) + os.sep + "config.json", "r"
        ) as json_file:
            config = json.load(json_file)

        self.server = Server(f'{config["url"]}:{config["port"]}')
        try:
            self.connection = Connection(
                self.server, user=config["user"], password=config["password"], auto_bind=True
            )
        except LDAPBindError:
            self.connection = Connection(
                self.server, user=config["user"], password=config["backup_password"], auto_bind=True
            )

    def get_subtree_entries(self, search_base, search_filter, attributes):
        """
        Retrieve LDAP entries in subtree based on the specified search parameters.

        Args:
            search_base (str): The base DN (Distinguished Name) for the search.
            search_filter (str): The LDAP filter string for the search.
            attributes (list): List of attributes to retrieve for each entry.

        Returns:
            list: A list of LDAP entries matching the search criteria.
        """
        self.connection.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=attributes,
        )
        entries = self.connection.entries
        return entries

    def auth(self, username, password):
        """
        Authenticate a user against the LDAP server

        Args:
            username (str): The username of user
            password (str): The password associated with the username

        Returns: True if successful, False otherwise.
        """

        user = f"fihtdc\\{username}"

        auth_conn = Connection(self.server, user=user, password=password)

        if auth_conn.bind():
            print("LDAP authentication successful")
            return True
        else:
            print("LDAP authentication failed. Invalid username or password.")
            return False

    def is_user_in_whitelist(
            self, username, condition, condition_list
    ):
        """
        Check if user is whitelisted based on a specified condition

        Args:
            username (str): The username of user
            condition (str): LDAP attribute condition
            condition_list (list): List of allowed values for the specified condition

        Returns:
            - True if user is whitelisted, False otherwise.
        """

        entries = self.get_subtree_entries(
            search_base="dc=fihtdc,dc=com",
            search_filter=f"(sAMAccountName={username})",
            attributes=[condition],
        )

        if entries[0][condition] in condition_list:
            print(f"User is in whitelist {condition}={condition_list}")
            return True
        else:
            print(f"User is not in whitelist {condition}={condition_list}")
            return False

    def whitelist_auth(self, whitelist_table, username, password):
        """
        Authenticate user based on department or personal permissions

        Args:
            whitelist_table (str): The MySQL whitelist table name
            username (str): The username of user
            password (str): The password associated with the username

        Returns: bool: True if successful, False otherwise.
        """
        whitelist_db = myDB("ldap")
        condition_dict = {"department": "department", "personal": "sAMAccountName"}

        if self.auth(username, password):
            for auth_type in ["department", "personal"]:
                search_results = whitelist_db.select_data(
                    whitelist_table, ["user"], f"where type = '{auth_type}'"
                )
                condition_list = (
                    list(chain.from_iterable(search_results)) if search_results else []
                )

                if self.is_user_in_whitelist(
                        username=username,
                        condition=condition_dict[auth_type],
                        condition_list=condition_list,
                ):
                    return True
        return False