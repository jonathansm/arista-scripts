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