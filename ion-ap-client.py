#!/usr/bin/env python3
"""
This is a command-line client for ion-AP.

It serves as both a tool for command-line operations, and as an example
for building interfaces with the ion-AP API.

It can call the standard sending/receiving endpoints

Currently, this tool only works with the ion-AP test instance.

You can set your API key in either the IONAP_API_KEY environment variable,
or the file ~/.ionap.conf
"""

# Copyright (c) 2021 Ionite
# License: MIT
# See LICENSE file for details

import argparse
import configparser
from datetime import datetime
import json
import os
import sys

import requests

API_VERSION = "0.3"
DEFAULT_BASE_URL = "https://test.ion-ap.net/api/"
DEFAULT_CONFIG_FILE = os.path.abspath(os.path.expanduser("~/.ion-ap-client.conf"))


class IonAPClientError(Exception):
    pass


class IonAPClient:
    def __init__(self, config_file=None, json_output=False, verbose=False):
        self.config_file = config_file
        self.json_output = json_output
        self.verbose = verbose

        self.config = configparser.ConfigParser()
        self.read_config()

        os_api_key = os.getenv("IONAP_API_KEY")
        if os_api_key is not None:
            self.api_key = os_api_key
        else:
            self.api_key = self.config.get('ionap', 'api_key')

        self.api_url = self.config.get('ionap', 'api_url')
        if not self.api_url.endswith('/'):
            self.api_url += '/'
        self.api_url += "%s/" % API_VERSION

    def read_config(self):
        if self.config_file is None:
            self.config_file = DEFAULT_CONFIG_FILE
        self.config['ionap'] = {
            'api_key': '<api key>',
            'api_url': DEFAULT_BASE_URL
        }
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            if self.verbose:
                print("Read configuration file %s" % self.config_file)
        else:
            if self.verbose:
                print("Configuration file %s does not exist, not reading configuration" % self.config_file)

    #
    # Helper methods
    #
    def request(self, method, path, data=None, headers=None):
        if self.api_key is None or self.api_key == '<api key>':
            raise IonAPClientError(
                "API key not set, please create a configuration file or set an environment variable IONAP_API_KEY")

        if headers is None:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        headers['Authorization'] = 'Token %s' % self.api_key

        url = "%s%s" % (self.api_url, path)

        if self.verbose:
            print("Request: %s %s" % (method, url))
            print("Headers:")
            for k, v in headers.items():
                # Print all tokens as-is, except the authorization token
                if k == "Authorization":
                    print("  Authorization: Token <api key>")
                else:
                    print("  %s: %s" % (k, v))

        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, data=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise IonAPClientError("Did not get a response object from requests library")

        if 200 <= response.status_code < 300:
            try:
                response_data = response.json()
                if self.json_output:
                    print(json.dumps(response_data, indent=2))
                    return None
            except json.decoder.JSONDecodeError:
                response_data = response.content.decode('utf-8')
            return response_data
        else:
            print("Error response: %d" % response.status_code)
            try:
                response_data = response.json()
                print(json.dumps(response_data, indent=2))
            except json.decoder.JSONDecodeError:
                response_data = response.content.decode('utf-8')
                print(response_data)
            return None

    def write_default_config(self):
        if os.path.exists(self.config_file):
            print("Error: %s already exists, not overwriting with defaults" % self.config_file)
        else:
            with open(self.config_file, "w") as output_file:
                self.config.write(output_file)
                print("Default configuration written to %s" % self.config_file)
            os.chmod(self.config_file, 0o600)

    #
    # Main functionality
    #
    def send_document(self, document_data, args):
        path = "send/document/"
        params = []
        if args.sender:
            sender = args.sender
            if sender.find("::") < 0:
                sender = "iso6523-actorid-upis::%s" % sender
            params.append("sender=%s" % sender)
        if args.receiver:
            receiver = args.receiver
            if receiver.find("::") < 0:
                receiver = "iso6523-actorid-upis::%s" % receiver
            params.append("receiver=%s" % receiver)
        if args.process_id:
            params.append("process_id=%s" % args.process_id)
        if args.document_id:
            params.append("document_id=%s" % args.document_id)
        if len(params) > 0:
            path += "?%s" % "&".join(params)
        method = "POST"
        headers = {
            'Content-Type': 'application/xml',
            'Accept': 'application/json'
        }
        result = self.request(method, path, data=document_data, headers=headers)
        return result

    def send_sbdh(self, document_data):
        path = "send/sbdh/"
        method = "POST"
        headers = {
            'Content-Type': 'application/xml',
            'Accept': 'application/json'
        }
        result = self.request(method, path, data=document_data, headers=headers)
        return result

    def send_status_list(self, page, page_size):
        path = "send/transactions/?page=%d&page_size=%d" % (page, page_size)
        method = "GET"
        result = self.request(method, path)
        if result:
            elements = result["results"]
            total = result["count"]
            if len(elements) > 0:
                first = 1 + (page_size * (page - 1))
                last = first + len(elements) - 1
            else:
                first = 0
                last = 0

            print("Showing %d-%d of %d transactions" % (first, last, total))
            for element in elements:
                print("%s\t%s\t%s" % (element["transaction_id"], element["status"], element["created_on"]))

    def send_status_single(self, transaction_id):
        path = "send/transactions/%s" % transaction_id
        method = "GET"
        result = self.request(method, path)
        if result:
            print("%s\t%s\t%s" % (result["transaction_id"], result["status"], result["created_on"]))

    def send_status_document(self, transaction_id):
        path = "send/transactions/%s/document" % transaction_id
        method = "GET"
        headers = {'Accept': 'application/xml'}
        document = self.request(method, path, headers=headers)
        print(document)

    def send_status_receipt(self, transaction_id):
        path = "send/transactions/%s/receipt" % transaction_id
        method = "GET"
        headers = {'Accept': 'application/xml'}
        document = self.request(method, path, headers=headers)
        print(document)

    def send_status_metadata(self, transaction_id):
        path = "send/transactions/%s/metadata/" % transaction_id
        method = "GET"
        result = self.request(method, path)
        if result:
            print("Sender:   %s::%s" % (result["sender_authority"], result["sender"]))
            print("Receiver: %s::%s" % (result["receiver_authority"], result["receiver"]))
            print("Type:     %s" % (result["document_identification_type"]))
            print("Process:  %s" % (result["business_scope_process_id"]))

    def send_status_delete(self, transaction_id):
        path = "send/transactions/%s/" % transaction_id
        method = "DELETE"
        self.request(method, path)

    def receive_list(self, page, page_size):
        path = "receive/transactions/?page=%d&page_size=%d" % (page, page_size)
        method = "GET"
        result = self.request(method, path)
        if result:
            elements = result["results"]
            total = result["count"]
            if len(elements) > 0:
                first = 1 + (page_size * (page - 1))
                last = first + len(elements) - 1
            else:
                first = 0
                last = 0

            print("Showing %d-%d of %d transactions" % (first, last, total))
            for element in elements:
                #print("%s\t%s\t%s" % (element["transaction_id"], element["status"], element["created_on"]))
                date_str = element["created_on"].replace("Z", "+00:00")
                
                date = datetime.fromisoformat(date_str)
                day = date.strftime("%Y-%m-%d")
                time = date.strftime("%H:%M")
                print("%s %s %s %s %s %s %s" % (
                    day, time,
                    element["document_sender"],
                    element["document_sender_name"],
                    element["document_identification_type"],
                    element["transaction_id"],
                    element["status"],
                ))
                #print(date.strftime("%Y-%m-%d"))

    def receive_single(self, transaction_id):
        path = "receive/transactions/%s" % transaction_id
        method = "GET"
        result = self.request(method, path)
        if result:
            print("%s\t%s\t%s" % (result["transaction_id"], result["status"], result["created_on"]))

    def receive_document(self, transaction_id):
        path = "receive/transactions/%s/document" % transaction_id
        method = "GET"
        headers = {'Accept': 'application/xml'}
        document = self.request(method, path, headers=headers)
        print(document)

    def receive_receipt(self, transaction_id):
        path = "receive/transactions/%s/receipt" % transaction_id
        method = "GET"
        headers = {'Accept': 'application/xml'}
        document = self.request(method, path, headers=headers)
        print(document)

    def receive_metadata(self, transaction_id):
        path = "receive/transactions/%s/metadata/" % transaction_id
        method = "GET"
        result = self.request(method, path)
        if result:
            print("Sender:   %s::%s" % (result["sender_authority"], result["sender"]))
            print("Receiver: %s::%s" % (result["receiver_authority"], result["receiver"]))
            print("Type:     %s" % (result["document_identification_type"]))
            print("Process:  %s" % (result["business_scope_process_id"]))

    def receive_delete(self, transaction_id):
        path = "receive/transactions/%s/" % transaction_id
        method = "DELETE"
        self.request(method, path)


class CommandLine:

    def __init__(self):
        parser = argparse.ArgumentParser(
            description="ion-AP API client",
            usage="""ionap_client.py <main command> [<args>]

Main commands:
    send            Send documents and retrieve status of send transactions
    send_status     View and retrieve the status and details of outgoing
                    transactions and documents
    receive         View and retrieve the status and details of incoming
                    transactions and documents
    create_config   Create an initial default config file

Use ion_ap_client <main command> -h for more details about the specific command.
    """)
        parser.add_argument("command", help="The main command to run")
        parser.add_argument("-c", "--config", help="Use the specified configuration file")
        parser.add_argument("-j", "--json", action="store_true", help="Print output as JSON")
        parser.add_argument("-v", "--verbose", action="store_true",
                            help="Verbose mode, print API actions and sent data as well")

        # Get the global options and command argument from sys
        main_args = []
        self.rest_args = []
        main_command_read = False

        args = sys.argv[1:]
        while len(args) > 0:
            arg = args.pop(0)
            if arg in ['-c', '--config']:
                main_args.append(arg)
                if len(args) > 0:
                    main_args.append(args.pop(0))
            elif arg in ['-j', '--json', '-v', '--verbose'] and arg not in main_args:
                main_args.append(arg)
            elif not main_command_read:
                main_args.append(arg)
                main_command_read = True
            else:
                self.rest_args.append(arg)

        args = parser.parse_args(main_args)

        # use dispatch pattern to invoke method with same name
        try:
            cmd = getattr(self, args.command)
        except AttributeError:
            print("Unknown command: %s" % args.command)
            sys.exit(2)

        self.api_client = IonAPClient(args.config, args.json, args.verbose)
        cmd()

    def send(self):
        parser = argparse.ArgumentParser(
            description="ion-AP API send document",
            usage="""ionap_client.py send <filename> [<args>]
""")
        parser.add_argument("filename", help="The XML document to send")
        parser.add_argument("--sender",
                            help="The sender identifier (in the form 0106:12345678 or "
                                 "iso6523-actorid-upis::0106:12345678")
        parser.add_argument("--receiver",
                            help="The receiver identifier (in the form 0106:12345678 or "
                                 "iso6523-actorid-upis::0106:12345678")
        parser.add_argument("--process-id",
                            help="The process id (such as "
                                 "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0)")
        parser.add_argument("--document-id",
                            help="The full document id (document type, root element, "
                                 "customization id and version)")

        args = parser.parse_args(self.rest_args)

        with open(args.filename, 'r') as infile:
            document_data = infile.read()
        result = self.api_client.send_document(document_data, args)
        if result:
            print("Status: %s Transaction id %s" % (result["status"], result["transaction_id"]))

    def send_sbdh(self):
        parser = argparse.ArgumentParser(
            description="ion-AP API send document (full SBDH)",
            usage="""ionap_client.py send <filename> [<args>]
""")
        parser.add_argument("filename", help="The XML document to send")

        args = parser.parse_args(self.rest_args)
        with open(args.filename, 'r') as infile:
            document_data = infile.read()
        result = self.api_client.send_sbdh(document_data)
        if result:
            print("Status: %s Transaction id %s" % (result["status"], result["transaction_id"]))

    def send_status(self):
        parser = argparse.ArgumentParser(
            description="ion-AP API send operations",
            usage="""ionap_client.py send_status <transaction> <command> [<args>]

Commands:
  document: Retrieve the XML document that was sent
  receipt: Retrieve the receipt that the receiving access point sent
  metadata: Retrieve metadata of the transaction (sender, receiver, etc.)
  delete: Delete the transaction
""")
        parser.add_argument("transaction",
                            help="The transaction ID to get information or data from, "
                                 "or a command. Leave empty for a list of send transactions",
                            nargs='?')
        parser.add_argument("command", help="A command to run on the transaction", nargs='?')
        parser.add_argument("-p", "--page", help="The page to show when listing transactions", type=int, default=1)
        parser.add_argument("-s", "--page-size", help="The number of items to show when listing transactions", type=int,
                            default=10)
        args = parser.parse_args(self.rest_args)

        if args.transaction is None:
            self.api_client.send_status_list(page=args.page, page_size=args.page_size)
        else:
            if args.command is None:
                self.api_client.send_status_single(args.transaction)
            elif args.command == "document":
                self.api_client.send_status_document(args.transaction)
            elif args.command == "receipt":
                self.api_client.send_status_receipt(args.transaction)
            elif args.command == "metadata":
                self.api_client.send_status_metadata(args.transaction)
            elif args.command == "delete":
                self.api_client.send_status_delete(args.transaction)
            else:
                print("Unknown command: %s" % args.command)

    def receive(self):
        parser = argparse.ArgumentParser(
            description="ion-AP API receive operations",
            usage="""ionap_client.py receive <transaction id> <command> [<args>]

Commands:
  document: Retrieve the XML document that was sent
  receipt: Retrieve the receipt that the receiving access point sent
  metadata: Retrieve metadata of the transaction (sender, receiver, etc.)
  delete: Delete the transaction
""")
        parser.add_argument("transaction",
                            help="The transaction ID to get information or data from. "
                                 "Leave empty for a list of transactions",
                            nargs='?')
        parser.add_argument("command", help="A command to run on the transaction", nargs='?')
        parser.add_argument("-p", "--page", help="The page to show when listing transactions", type=int, default=1)
        parser.add_argument("-s", "--page-size", help="The number of items to show when listing transactions", type=int,
                            default=10)
        # parser.add_argument("--json", action="store_true", help="Print output as JSON")
        args = parser.parse_args(self.rest_args)

        if args.transaction is None:
            self.api_client.receive_list(page=args.page, page_size=args.page_size)
        else:
            if args.command is None:
                self.api_client.receive_single(args.transaction)
            elif args.command == "document":
                self.api_client.receive_document(args.transaction)
            elif args.command == "receipt":
                self.api_client.receive_receipt(args.transaction)
            elif args.command == "metadata":
                self.api_client.receive_metadata(args.transaction)
            elif args.command == "delete":
                self.api_client.receive_delete(args.transaction)
            else:
                print("Unknown command: %s" % args.command)

    def create_config(self):
        self.api_client.write_default_config()


if __name__ == '__main__':
    try:
        client = CommandLine()
    except IonAPClientError as iace:
        print("Error: %s" % str(iace))
