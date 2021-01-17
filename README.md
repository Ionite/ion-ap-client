# ion-AP API client tool

This is a client tool for the ion-AP API.

It serves as both a tool for command-line operations, and as an example
for building interfaces with the ion-AP API.

# Requirements

- the Python requests library
- An account with an api key on test.ion-ap.net

# Usage

Use ion-ap-client.py -h to see the main command and global options.

Use ion-ap-client.py <command> -h to see specific command usage.

# Installation

- Clone this repository
    git clone https://github.com/ionite/ion-ap-client
    cd ion-ap-client
- Install the requests library, globally or in a virtual environment
    sudo pip3 install requests
- Create initial configuration
    ./ion-ap-client.py create_config
- Set your API key in the configuration file
    vi ~/.ion-ap-client

You are now ready to go. To see whether you have already received
any documents:
    ./ion-ap-client receive

# Examples

All commands support the global options: -j (print JSON response from
server instead of parsed results. In the case where XML documents are
returned, the XML is printed), and -v (print request and headers
sent to server).

Create an initial default configuration file, where you can set your
API key.

    > ./ion-ap-client.py create_config
    Default configuration written to /home/user/.ion-ap-client.conf


Retrieve the most recent incoming transactions (by default, up to ten)

    > ./ion-ap-client.py receive
    Showing 1-4 of 4 transactions
    3cdb0ab8-590c-11eb-82f6-525400ffdadc    new     2021-01-17T21:37:48.769630Z
    e582fdce-56af-11eb-82f6-525400ffdadc    read    2021-01-14T21:31:44.380816Z
    e8ce2e18-574a-11eb-9357-40167ead2f63    read    2021-01-15T16:01:22.592128Z
    e68e5166-56ad-11eb-82f6-525400ffdadc    read    2021-01-14T21:17:27.097156Z

Retrieve the metadata information of one incoming transaction

    > ./ion-ap-client.py receive 3cdb0ab8-590c-11eb-82f6-525400ffdadc metadata
    Sender:   iso6523-actorid-upis::0106:72413514
    Receiver: iso6523-actorid-upis::0106:72413514
    Type:     Invoice
    Process:  urn:fdc:peppol.eu:2017:poacc:billing:01:1.0

Retrieve the incoming document

    > ./ion-ap-client.py receive 3cdb0ab8-590c-11eb-82f6-525400ffdadc document
    <Invoice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:qdt="urn:oasis:names:specification:ubl:schema:xsd:QualifiedDataTypes-2" xmlns:udt="urn:oasis:names:specification:ubl:schema:xsd:UnqualifiedDataTypes-2" xmlns:ccts="urn:un:unece:uncefact:documentation:2" xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2">
        <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
    <REST OF DOCUMENT LEFT OUT>

Delete the incoming transaction

    > ./ion-ap-client.py receive 3cdb0ab8-590c-11eb-82f6-525400ffdadc delete


Send an XML document

    > ./ion-ap-client.py send /tmp/document.xml
    Status: sent Transaction id f5647c40-590c-11eb-82f6-525400ffdadc

Retrieve a list of send transaction statuses

    > ./ion-ap-client.py send_status
    Showing 1-10 of 12 transactions
    f5647c40-590c-11eb-82f6-525400ffdadc	sent	2021-01-17T21:42:55.645197Z
    3cdb0ab8-590c-11eb-82f6-525400ffdadc	sent	2021-01-17T21:37:46.044693Z
    67d2b326-5752-11eb-82f6-525400ffdadc	sent	2021-01-15T16:55:00.579139Z
    e582fdce-56af-11eb-82f6-525400ffdadc	sent	2021-01-14T21:31:43.483742Z
    e68e5166-56ad-11eb-82f6-525400ffdadc	sent	2021-01-14T21:17:26.237728Z
    cc6a4cfe-56ad-11eb-82f6-525400ffdadc	error	2021-01-14T21:16:42.383952Z
    8dce74d4-56ad-11eb-82f6-525400ffdadc	sent	2021-01-14T21:14:57.341866Z
    d1a5a8d6-569d-11eb-82f6-525400ffdadc	sent	2021-01-14T19:22:19.215595Z
    c202fe06-569d-11eb-82f6-525400ffdadc	sent	2021-01-14T19:21:52.980897Z
    c03d5990-569d-11eb-82f6-525400ffdadc	sent	2021-01-14T19:21:50.010211Z


Retrieve the receipt of the send transaction

    ./ion-ap-client.py send_status f5647c40-590c-11eb-82f6-525400ffdadc receipt
    <?xml version="1.0" encoding="UTF-8"?><DeliveryNonDeliveryToRecipient xmlns="http://uri.etsi.org/02640/v2#" xmlns:ns2="http://uri.etsi.org/02231/v2#" xmlns:ns3="http://www.w3.org/2000/09/xmldsig#" xmlns:ns4="http://uri.etsi.org/01903/v1.3.2#" xmlns:ns5="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:ns6="http://www.w3.org/2001/04/xmlenc#" xmlns:ns7="http://peppol.eu/xsd/ticc/receipt/1.0" version="2"><EventCode>
    <REST OF DOCUMENT LEFT OUT>

Delete a send transaction 

    > ./ion-ap-client.py send_status f5647c40-590c-11eb-82f6-525400ffdadc delete

