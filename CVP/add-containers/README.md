# Bulk Add Containers
Quickly add one or multiple containers to CloudVision. The script will allow you to set the common container name, the starting number, and if you want that number padded with zeros. You can select the container you want these containers created under. 

## Example

```
 ./add-containers.py 
Please enter the IP Address or FQDN of CloudVision: 172.25.200.100
Username: admin
Password: 
Conntected to CloudVision!
Please select which container to add the containers to.
[1]: Tenant
[2]: Lab
[3]: Leafs
[4]: Spines
[5]: TapAgg
[6]: Staging
Container Number: 3
Container selected: Leafs
How many containers do you want to make? 11
Please enter the common name for the containers. Add the delmiator that will go in between the name and numbers i.e. space, dash, etc: VTEP-
What number do you want to start at? i.e. VTEP-1, VTEP-2
Starting Number [1]: 
Do you want the numbers padded with zeros? (i.e. VTEP-001): yes
How many digits do you want the number to be? Max is 4: 3
Sample of containers that will be created
VTEP-001
VTEP-002
VTEP-003
...
VTEP-011
Are you happy with the containers and ready to create them? yes
Creating container VTEP-001
Creating container VTEP-002
Creating container VTEP-003
Creating container VTEP-004
Creating container VTEP-005
Creating container VTEP-006
Creating container VTEP-007
Creating container VTEP-008
Creating container VTEP-009
Creating container VTEP-010
Creating container VTEP-011
```

### TO Do
* Add commandline options so you don't have to use the menu