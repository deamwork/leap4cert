#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import argparse
import os

import requests

INAP_API_TOKEN = os.getenv("INAP_API_TOKEN", default="FILL_ME")
INAP_API_BASE_URL = "https://inblue.inap.com/api/purchasing/v1/ssl-certs"
COMMON_HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {INAP_API_TOKEN}",
}

logger = logging.getLogger(__name__)

def get_list():
    response = requests.get(f'{INAP_API_BASE_URL}?limit=25&offset=0')


def initialize(hostname: str, first_name: str, last_name: str, email: str, phone: str) -> list[str]:
    try:
        response = requests.post(
            url=f'{INAP_API_BASE_URL}/initialize',
            json={
                "hostname": hostname,
                "contactFirstName": first_name,
                "contactLastName": last_name,
                "contactEmailAddress": email,
                "contactPhoneNumber": phone
            },
            headers=COMMON_HEADERS
        )

        if response.status_code != 200:
            raise Exception(f"Unable to fetch approve emails, response code[{response.status_code}] {response.json()}")

        resp = response.json()

        if resp['success'] is not True:
            raise Exception(f"Unable to fetch approve emails, response code[{response.status_code}] {response.json()}")

        logger.info(f"Order #{resp['certId']} created.")
        # logger.info(f"available approver email as follows, choose one: ")
        return resp["approverEmails"]
    except Exception as e:
        logger.critical(e)


def finalize(order_id: str, approver_email: str, csr: str) -> bool:
    try:
        response = requests.post(
            url=f'{INAP_API_BASE_URL}/{order_id}/finalize',
            json={
                "approverEmailAddress": approver_email,
                "csr": csr
            },
            headers=COMMON_HEADERS
        )

        if response.status_code != 200:
            raise Exception(f"Unable to fetch order status, maybe you should try again later, "
                            f"response code[{response.status_code}] {response.json()}")

        resp = response.json()

        if resp['success'] != "1":
            raise Exception(f"Unable to fetch order status, maybe you should try again later, "
                            f"response code[{response.status_code}] {response.json()}")

        logger.info(f"Order #{order_id} placed.")
        logger.info(f'Please check your inbox "{approver_email}" to finalize your certificate order.')
        # logger.info(f"available approver email as follows, choose one: ")
        return True
    except Exception as e:
        logger.critical(e)


def gather_info():
    hostname = input("Input domain which requires certificate: ").strip()
    first_name = input("Your first name: ").strip()
    last_name = input("Your last name: ").strip()
    email = input("Your email address (use to receive certificate): ").strip()
    phone = input("Your phone number: ").strip()
    return hostname, first_name, last_name, email, phone


def interactive_mode(dry_run: bool):
    pass


def automation_mode():
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser('leap4cert')
    parser.add_argument('--debug',
                        action='store_true',
                        help='Print debug info')
    parser.add_argument('--config',
                        default=None,
                        nargs='?',
                        help='run workflow with pre-defined config')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s v1.0.0')

    subprasers = parser.add_subparsers(dest='command')

    # sub cmd: order
    # fill domain and contact details to create certificate order
    order = subprasers.add_parser('order', help='create a certificate order')
    order.add_argument(
        '--dry-run',
        help='do not order, just pretend',
        action='store_true'
    )

    # sub cmd: finalize
    # fill csr and choose email to complete the DCV process
    finalize = subprasers.add_parser('finalize', help='finalize certificate order')
    finalize.add_argument('id', nargs=1, help='id of order to finalize')

    # parse it
    args = parser.parse_args()
    if args.debug:
        print("debug: " + str(args))
    if args.command == 'order':
        interactive_mode(dry_run=args.dry_run)
    elif args.command == 'finalize':
        print(f'processing for order #{args.id[0]}')

    # if not os.path.isfile(input_path):
    #     print('The path specified does not exist')
    #     sys.exit()
