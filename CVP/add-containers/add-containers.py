#!/usr/bin/env python

from __future__ import print_function
from getpass import getpass
import requests
import urllib3

try:
    input = raw_input
except NameError:
    pass


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
cvp = requests.Session()
url = ""

def connect(user, password):
    data = {
        "userId": user,
        "password": password}
    try:
        response = post_data(url + "/cvpservice/login/authenticate.do", data)
    except:
        return False

    if response.get("errorCode") == "112498":
        return False

    return True

def disconnect():
    response = post_data(url + "/cvpservice/login/logout.do", [])
def post_data(url, data):
    response = cvp.post(url, json=data, verify=False)

    return response.json()

def save_topo():
    post_data(url + "/cvpservice/provisioning/saveTopology.do", [])

def get_containers():
    response = cvp.get(url + "/cvpservice/inventory/containers")
    data = response.json()
    containers = []

    for container in data:
        if container.get("Name") != "Undefined":
            containers.append({"key":container.get("Key") , "name":container.get("Name") })

    return containers

def add_container(container_name, parent_name, parent_key):
    data = {
      "data": [
        {
          "info": "Adding Container",
          "infoPreview": "Adding Container",
          "action": "add",
          "nodeType": "container",
          "nodeId": "new_container",
          "toId": parent_key,
          "fromId": "",
          "nodeName": container_name,
          "toName": parent_name,
          "fromName": "",
          "toIdType": "container"}]}

    response = post_data(url + "/cvpservice/provisioning/addTempAction.do?nodeId=root&format=topology", data)
    save_topo()

def valid_int(num):
    try:
        int(num)
    except ValueError:
        return False

    return True

def buildMenu():
    containers = get_containers()
    container_params = {}
    print("Please select which container to add the containers to.")
    for i, container in enumerate(containers):
        print ("[" + str(i+1) + "]: " + container.get("name"))

    valid_container = False

    while valid_container == False:
        parent_cont = -1
        parent_container = input("Container Number: ")

        if not valid_int(parent_container):
            print("Not a valid choice!")
        else:
            parent_cont = int(parent_container)

        if parent_cont <= len(containers) and parent_cont >= 0:
            valid_container = True

    parent_container_dict = containers[parent_cont - 1]

    print("Container selected: " + parent_container_dict.get("name"))
    parent_container = parent_container_dict.get("name")
    parent_container_key = parent_container_dict.get("key")


    valid_amount = False
    while valid_amount == False:
        amount_int = -1
        amount = input("How many containers do you want to make? ")

        if not valid_int(amount):
            print("Please choose a number!")
        else:
            amount_int = int(amount)

        if amount_int > 0:
            valid_amount = True
        else:
            print("Must be greater than 0!")

    container_name_prefix = input("Please enter the common name for the containers. Add the delmiator that will go in between the name and numbers i.e. space, dash, etc: ")

    print("What number do you want to start at? i.e. " + container_name_prefix +  "1, "+ container_name_prefix +  "2")
    valid_start = False
    while valid_start == False:
        start_int = -1
        start = input("Starting Number [1]: ") or "1"

        if not valid_int(start):
            print("Please choose a number!")
        else:
            start_int = int(start)

        if start_int > 0:
            valid_start = True
        else:
            print("Must be greater than 0!")

    valid_padding = False
    while valid_padding == False:
        padding_anwser = input("Do you want the numbers padded with zeros? (i.e. " + container_name_prefix +  "00" + str(start_int) + "): ")
        if padding_anwser.lower() == "no":
            valid_padding = True
            padded_num = 0
        elif padding_anwser.lower() == "yes":
            valid_padding_num = False
            while valid_padding_num == False:
                
                padded_respone = input("How many digits do you want the number to be? Max is 4: ")

                if not valid_int(padded_respone):
                    print("Please choose a number!")
                else:
                    padded_num = int(padded_respone)

                if padded_num > 0 and padded_num <= 4:
                    valid_padding_num = True
                    valid_padding = True
                else:
                    print("Must be greater than 0 and less than 4!")
        else:
            print("Not a valid answer! Yes or No")

    print("Sample of containers that will be created")
    if amount_int <= 5:
        for i in range(amount_int):
            print("{}{}".format(container_name_prefix, str(start_int+i).zfill(padded_num)))
    else:
        for i in range(3):
            print("{}{}".format(container_name_prefix, str(start_int+i).zfill(padded_num)))
        print("...")
        print("{}{}".format(container_name_prefix, str(amount_int).zfill(padded_num)))

    container_params.update({"parent_container": parent_container})
    container_params.update({"parent_container_key": parent_container_key})
    container_params.update({"amount_int": amount_int})
    container_params.update({"container_name_prefix": container_name_prefix})
    container_params.update({"padded_num": padded_num})
    container_params.update({"start_int": start_int})

    while True:
        response = input("Are you happy with the containers and ready to create them? ")

        if response.lower() == "yes":
            return (True, container_params)
        elif response.lower() == "no":
            return (False, {})

    return (False, {})

connected = False
while connected == False:
    url = "https://"
    url += input("Please enter the IP Address or FQDN of CloudVision: ")
    username = input("Username: ")
    password = getpass("Password: ")

    connected = connect(username, password)

    if connected == False:
        print("Error connecting to " + url)

print("Conntected to CloudVision!")

containers_ready = False
while containers_ready == False:
    containers_ready, container_params = buildMenu()

for i in range(container_params.get("amount_int")):
    container_name = "{}{}".format(container_params.get("container_name_prefix"), str(container_params.get("start_int")+i).zfill(container_params.get("padded_num")))
    print("Creating container " + container_name)
    add_container(container_name, container_params.get("parent_container"), container_params.get("parent_container_key"))


disconnect()
