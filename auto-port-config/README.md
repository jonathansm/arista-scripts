# Arista Auto Port Config
This python script will configure interfaces based on the full mac address or OUI (Organizationally Unique Identifier). The script can be run remotely, or on the switch itself, it can also be automatically called when a device is plugged into the switch using the Event Handler.

## Config
The purposed config is by default stored in a file called `auto-port.conf` in the same directory as the script; this can be overridden by using the flag `-c`

This is how the file should be structured.

```
mac address or OUI
You can have single or multiple and can mix full addresses with OUIs

Config to apply

%DEFAULT%

config to apply
```

You can have several different interface configs based on separate mac addresses and or OUIs. 

The `%DEFAULT%` wildcard will be used if no mac address or OUI is found on the port. You can also not include the default wildcard, and no config change will happen if there is no mac address or OUI found.

See the example config file.

## Remotely
You can run this script remotely using the `-a` flag. For example
```
python auto-port-config.py -i Ethernet6 -a username:password@192.169.0.1
```

This will check the interface `Ethernet6` on the remote switch and make the config change if needed. If you wanted to check all interfaces, it would be super easy just to throw it into a bash loop.

## On Switch
You can run this on the switch from the CLI
```
bash python /mnt/flash/auto-port-config/auto-port-config.py -i Ethernet6
```

What is even cooler is you can set this up to run automatically when a device is plugged in using an Event Handler

### Event Handler
The event-handler script was written with the help from Mihyar Baroudi. Currently, there is no easy way of getting the interface on which the trigger was called. Mihyar helped me with this workaround, and hopefully, they will add in a better way of getting the interface.

```
event-handler AutoConfig
   trigger on-intf Ethernet1-48 operstatus
   action bash
#!/usr/bin/env python
import os, json, subprocess, time
intf_state_path = '/var/run/intf_state_path.json'
intf_state = {}
old_intf_state = {}
if os.path.exists( intf_state_path ):
    with open( intf_state_path ) as intfStateFile:
        old_intf_state = json.load( intfStateFile )
for env, intf_name in os.environ.items():
    if env.startswith( 'INTF_' ):
        intf_state[ intf_name ] = os.environ[ 'OPERSTATE_' + env[5:] ]
        with open( intf_state_path , 'w' ) as intfStateFile:
            json.dump( intf_state , intfStateFile )
for intf_name, current_state in intf_state.items():
    old_state = old_intf_state.get( intf_name )
    if old_state != current_state and current_state == "linkup":
        time.sleep(30)
        subprocess.check_output(['bash','-c', "python /mnt/flash/auto-port-config/auto-port-config.py -i " + intf_name])
EOF
   delay 0
   asynchronous
   timeout 40
```

Create an event handler that will call the python command if the interface state changes from down to up. You can copy that snippet of code directly into the switch in config mode, assuming your script is saved into a folder called `auto-port-config` on your flash.

I'll go through what we are creating up above.

First, create the event handler.

```
event-handler AutoConfig
```

Second, set what we want to trigger on. You can select any range of interfaces you want.

```
trigger on-intf Ethernet1-48 operstatus
```

Then we set what we want as the action. Basically, what is happening is it saving the current state of every interface. Then when the script is called, we look at what it has saved and then what has changed and compare them. If the state went from down to up, our python script runs. 

You will see that there is a `sleep` time set to 30 seconds. What that is doing is its waiting so that the switch can populate the mac-address-table for the interfaces that the device was just plugged into. You can play around with that time to your liking. I have found with my testing that 30 seconds worked pretty well most of the time. 

```
 delay 0
 asynchronous
 timeout 40
```

After the action is set, then set the delay of the script to 0, and set the event handler to run asynchronously; that way, if a device is plugged in while other devices are plugged in, the switch is not waiting for the one to finish to run the others. Each event trigger will run independently of each other. Set the delay to 0 since the bulk of the trigger is saving and checking the interface status. The script only waits the 30 seconds if the state changed from down to up.

Set a timeout of 40 seconds, in case the script gets locked up, the switch will kill the process in 40 seconds.