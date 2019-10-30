#!/usr/bin/env python

"""Auto Port Config
This python script will configure interfaces based on the full mac address or OUI (Organizationally Unique Identifier). 
The script can be run remotely, or on the switch itself, it can also be automatically called when a device is plugged 
into the switch using the Event Handler.
"""


from __future__ import print_function
import argparse
import sys
from jsonrpclib import Server
import ssl
import collections
import os
import time

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

switch = Server( "unix:/var/run/command-api.sock")
apply_default_config = False

def main():
    parser = argparse.ArgumentParser(description='Auto Port Config')

    interfaceInfo = parser.add_mutually_exclusive_group(required=True)

    interfaceInfo.add_argument('-i', action='store', dest='inter', help='Interface that has changed state')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    parser.add_argument('-c', action='store', dest='config', default=dir_path + '/auto-port.conf', help='File containting the ouis and config to apply. Default is auto-port.conf in same dir as script')
    parser.add_argument('-a', action='store', dest='address', help='The username password and address to the switch. username:password@ipaddress')

    results = parser.parse_args()

    if results.address:
        global switch 
        switch = Server("https://{}/command-api".format(results.address))


    ouis = []
    interface_config = []

    parse_config_file(results.config, ouis, interface_config)
    

    mac_index = check_interface_macs(results.inter, ouis)

    if mac_index != -99 and apply_default_config:
        # Check if the interface config matches the purposed config or if there is a default config, quit if it does.
        if check_interface_config(results.inter, interface_config[mac_index]) and not apply_default_config:
            quit()

        config_interface(interface_config[mac_index], results.inter)


def parse_config_file(_config_file, _ouis, _interface_config):
    """Parses the purposed configuration file

    If the default wildcard is used then the global variable apply_default_config is set to True
    This will apply a default config to a interface. If not used then we ignore an interface that doesn't match

    Parameters
    ----------
    _config_file : str
        Path to the configuration file
    _ouis : array of lists
        All of the ouis or mac addresses. Each section is a index of the array stored in a list
    _interface_config : array of lists
        The config for the matching interfaces. Each config section is a index of the array stored in a list

    """

    file = open(_config_file, "r")
    line = file.readline()

    while line:
        oui = []
        cmds = []

        while line:
            if line == '\n':
                break
            if line == "%DEFAULT%\n":
                global apply_default_config
                apply_default_config = True

            oui.append(clean_mac_address(line))    
            line = file.readline()

        _ouis.append(oui)    
        line = file.readline()

        while line:
            if line == '\n':
                break

            cmds.append(line.strip())    
            line = file.readline()

        _interface_config.append(cmds)

        line = file.readline() 
 
    file.close()

"""

"""
def check_interface_macs(_interface, _ouis):
    """Checks to see if any OUIs or mac addresses are located on an interface

    Pulls all mac address from the mac address table for an interface. 

    Parameters
    ----------
    _interface : str
        The interface to check
    _ouis : array of lists
        All of the ouis or mac addresses. Each section is a index of the array stored in a list

    Returns
    ----------
    The index of the array in which the OUI or mac address matches from the _oui array.
    Will return a -99 if no mac address, OUI or not using a default config.
    """

    mac_addresses = []

    response = runCMD(["show mac address-table interface " + _interface])

    for mac_address in response[1]['unicastTable']['tableEntries']:

        mac_addresses.append(clean_mac_address(mac_address['macAddress']).encode("utf-8"))
    
    for index, ouis in enumerate(_ouis):
        # Search for more specific mac address first
        if any(item in mac_addresses for item in ouis):
            return index

        for oui in ouis:
            if any([ mac.startswith(oui) for mac in mac_addresses]):
                return index

    if apply_default_config:
        if any(item in ["%default%"] for item in ouis):
            return index

    return -99

def check_interface_config(_interface, _int_config):
    """Checks to see if the interface already has the correct config

    Parameters
    ----------
    _interface : str
        The interface to check
    _int_config : list
        What the config of the interace should be

    Returns
    ----------
    Bool. True if the config is the same. False the configs do not match and the interface needs to be configured.
    """

    response = runCMD(["show running-config interfaces  " + _interface], 'text')

    # Clean up config from switch and put it into a list
    config = response[1]["output"].split("\n")
    config = [line.strip().encode("utf-8") for line in config if line]
    del config[:1]

    return set(config) == set(_int_config)

def config_interface(_config, _interface):
    """Sets up command to send to the switch to configure the interface.

    Parameters
    ----------
    _config : list
        The config to apply
    _interface : str
        The interface to configure

    """

    runCMD(["configure", "default interface " + _interface, "interface " + _interface] + _config)


def clean_mac_address(mac):
    """Cleans up the mac address. Removes any standard delimiter and converts it to lowercase

    Parameters
    ----------
    mac : str
        The mac address that needs to be sanitized

    Returns
    ----------
    The sanitized mac address
    """

    return mac.replace(':','').replace('.','').replace('-','').strip().lower()

def runCMD(_cmd, _format='json'):
    """Sends a command to the switch.

    Parameters
    ----------
    _cmd : list
        The command to be ran.
    _format : str, optional
        What format do you want in return. Default is json. Some commands like `show run` do not support json, you have to set the 
        format to text for it to work.

    Returns
    ----------
    The output from the switch.
    """

    try:
        return switch.runCmds( version = 1, cmds = ["enable"] + _cmd, format=_format)
    except:
        print("Error with connecting to switch! Please try again.")
        quit()

if __name__ == "__main__":
    if sys.version_info[:2] <= (2, 7):
        input = raw_input
    main()