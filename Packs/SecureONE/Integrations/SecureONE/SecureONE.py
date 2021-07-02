"""Base Integration for Cortex XSOAR (aka Demisto)

This is an empty Integration with some basic structure according
to the code conventions.

MAKE SURE YOU REVIEW/REPLACE ALL THE COMMENTS MARKED AS "TODO"

Developer Documentation: https://xsoar.pan.dev/docs/welcome
Code Conventions: https://xsoar.pan.dev/docs/integrations/code-conventions
Linting: https://xsoar.pan.dev/docs/integrations/linting

This is an empty structure file. Check an example at;
https://github.com/demisto/content/blob/master/Packs/HelloWorld/Integrations/HelloWorld/HelloWorld.py

"""

import demistomock as demisto
from CommonServerPython import *  # noqa # pylint: disable=unused-wildcard-import
from CommonServerUserPython import *  # noqa

import requests
import traceback
from typing import Dict, Any

# Disable insecure warnings
requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member


''' CONSTANTS '''

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'  # ISO8601 format with UTC, default in XSOAR

''' CLIENT CLASS '''


class Client(BaseClient):
    """Client class to interact with the service API

    This Client implements API calls, and does not contain any XSOAR logic.
    Should only do requests and return data.
    It inherits from BaseClient defined in CommonServer Python.
    Most calls use _http_request() that handles proxy, SSL verification, etc.
    For this  implementation, no special attributes defined
    """

    def get_sessions_for_machine(self, machine_name: str, domain_name: str ) -> Dict[str, Any]:
        api = f'/risk/machine'
        print(self._base_url)
        response = self._http_request(
            method='GET',
            url_suffix=api,
            params={
                'machine_name': machine_name,
                'domain_name': domain_name
            }
        )
        return response

    def get_sessions_for_account(self, account: str) -> Dict[str, Any]:
        api = f'/risk/account'
        response = self._http_request(
            method='GET',
            url_suffix=api,
            params={
                'tstart': '1617910914',
                'tend': '1617910920',
                'account_name': account,
                'domain_name': "trash",
                'users': True,
                'groups': True,
                'accounts': True,
                'persistent': True,
                'jita': True,
                'access_history': True
            }
        )
        return response

    def get_sessions_for_group(self, group: str) -> Dict[str, Any]:
        api = f'/risk/group'
        response = self._http_request(
            method='GET',
            url_suffix=api,
            params={
                'tstart': '1617910914',
                'tend': '1617910920',
                'group_name': group,
                'domain_name': "trash",
                'users': True,
                'groups': True,
                'accounts': True,
                'persistent': True,
                'jita': True,
                'access_history': True
            }
        )
        return response


''' HELPER FUNCTIONS '''

# TODO: ADD HERE ANY HELPER FUNCTION YOU MIGHT NEED (if any)

''' COMMAND FUNCTIONS '''


def execute_test_module_command(client: Client) -> str:
    """Tests API connectivity and authentication'

    Returning 'ok' indicates that the integration works like it is supposed to.
    Connection to the service is successful.
    Raises exceptions if something goes wrong.

    :type client: ``Client``
    :param Client: client to use

    :return: 'ok' if test passed, anything else will fail the test.
    :rtype: ``str``
    """

    message: str = ''
    try:
        # TODO: ADD HERE some code to test connectivity and authentication to your service.
        # This  should validate all the inputs given in the integration configuration panel,
        # either manually or by using an API that uses them.
        message = 'ok'
    except DemistoException as e:
        if 'Forbidden' in str(e) or 'Authorization' in str(e):  # TODO: make sure you capture authentication errors
            message = 'Authorization Error: make sure API Key is correctly set'
        else:
            raise e
    return message


def execute_risk_for_machine_command(client: Client, machine_name: str, domain_name: str) -> CommandResults:
    if not machine_name:
        raise ValueError('machine name not specified')

    if not domain_name:
        raise ValueError('machine name not specified')

    # Call the Client function and get the raw response
    result = client.get_sessions_for_machine(machine_name, domain_name)

    return CommandResults(
        outputs_prefix='Secureone.Sessions',
        outputs_key_field='machine_id',
        outputs=result,
    )


def execute_risk_for_account_command(client: Client, account: str) -> CommandResults:
    if not account:
        raise ValueError('account name not specified')

    # Call the Client function and get the raw response
    result = client.get_sessions_for_account(account)

    return CommandResults(
        outputs_prefix='Secureone.Access',
        outputs_key_field='account_id',
        outputs=result,
    )


def execute_risk_for_group_command(client: Client, group: str) -> CommandResults:
    if not group:
        raise ValueError('group name not specified')

    # Call the Client function and get the raw response
    result = client.get_sessions_for_group(group)

    return CommandResults(
        outputs_prefix='Secureone.GroupAccess',
        outputs_key_field='group_id',
        outputs=result,
    )

# TODO: ADD additional command functions that translate XSOAR inputs/outputs to Client


''' MAIN FUNCTION '''


def main() -> None:
    """main function, parses params and runs command functions

    :return:
    :rtype:
    """

    # TODO: make sure you properly handle authentication
    # api_key = demisto.params().get('apikey')

    # get the service API url
    base_url = demisto.params()['url']

    # if your Client class inherits from BaseClient, SSL verification is
    # handled out of the box by it, just pass ``verify_certificate`` to
    # the Client constructor
    verify_certificate = not demisto.params().get('insecure', False)

    # if your Client class inherits from BaseClient, system proxy is handled
    # out of the box by it, just pass ``proxy`` to the Client constructor
    proxy = demisto.params().get('proxy', False)

    demisto.debug(f'Command being called is {demisto.command()}')
    try:

        # TODO: Make sure you add the proper headers for authentication
        # (i.e. "Authorization": {api key})
        headers: Dict = {}

        client = Client(
            base_url=base_url,
            verify=verify_certificate,
            headers=headers,
            proxy=proxy)

        command_methods = {
            'test-module': lambda: execute_test_module_command(client),
            'secureone-get-machine-risk': lambda: execute_risk_for_machine_command(client, demisto.params().get('machine_name','TRASH'), demisto.params().get('domain_name', 'RTEST')),
            'secureone-get-account-risk': lambda: execute_risk_for_account_command(client, demisto.args.get("account_name")),
            'secureone-get-group-risk': lambda: execute_risk_for_group_command(client, demisto.args.get("group_name"))
        }
        command_method = command_methods.get(demisto.command())

        if not command_method:
            raise DemistoException(f'command not recognised - {demisto.command()}')

        result = command_method()
        if result:
            return_results(result)

    # Log exceptions and return errors
    except Exception as e:
        demisto.error(traceback.format_exc())  # print the traceback
        return_error(f'Failed to execute {demisto.command()} command.\nError:\n{str(e)}')


''' ENTRY POINT '''


if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
