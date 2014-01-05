#!/usr/bin/env python2.7

import boto.ec2
import time
import argparse
import sys

#Get region identifiers
def list_regions():
	regions = boto.ec2.regions()
	for i in regions:
		print i.name

#Set region for ref in other functions
def set_region(region='us-west-2'):
	return boto.ec2.connect_to_region(region)

#Launch EC2 instances with quick defaults
def launch_instance(num=1, instance_type='t1.micro', tag='QuickLaunched', ami='ami-be1c848e', 
	sg='LinuxSG', key='KeyPairName'):
	conn = set_region()
	reservation = conn.run_instances(ami, key_name=key, instance_type=instance_type, 
		security_groups=[sg], max_count=num)
	while num > 0:        
         instance = reservation.instances[0] 
    	 instance.update()
    	 while instance.state == "pending":
            print "Launching, please wait"
            time.sleep(10)
            instance.update()
            
         instance.add_tag("Name", tag)
         print 'Ready to connect at: %s' % instance.public_dns_name
            #return instance.id #I want to make this a default for terminate_instance
         instance = reservation.instances.pop(0)
         num -= 1

#Terminate EC2 instances
def terminate_instance(instance_id):
	conn = set_region()
	conn.terminate_instances(instance_ids=[instance_id])
        print 'Terminating %s' %instance_id

#Terminate all instances w/o tags
def terminator():
	conn = set_region()
	instances = conn.get_all_instances()
	#print instances # debuging
	for reserv in instances:
		for inst in reserv.instances:
			if inst.tags:
				pass
			else:
				print 'No tag, terminating %s' % inst
				inst.terminate()
        else:
            print "All other instances are tagged"

# Currently only number of instances is supported from launch_instance() function
# Terminate parser not implemented
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='EC2QuickManager is a simple Python script to help ease common EC2 tasks')
    parser.add_argument('--verbose', action='store_true',
                        help='show addtional output when runnning commands')
    parser.add_argument('--action', action='append', help='available actions are: launch, terminate, tag_terminator and regions. '
                                                          'launch - Quickly launch an EC2 instance and get the connection details; '
                                                          'terminate - Quickly terminate an EC2 instance.  Default is previously launched instance; '
                                                          'tag_terminator - Terminates any and all EC2 instances which are not tagged; '
                                                          'regions - Quick reference to regions for use in other actions')
    parser.add_argument('--number', action='store', type=int, help='Used to provide the number of instances to launch. ') 
    parser.add_argument('-y', action='store_true')
    args = parser.parse_args()

    if args.action:
        action = args.action[0]
        if action == 'launch':
    	    if args.number >= 0:
                num = args.number
                launch_instance(num)
            else:
                print "To launch more than 1 instance, use --num X" 
                launch_instance()
        elif action == 'terminate':
            if args.y:
                terminate_instance() #not implemented
            else:
                print "You must add -y when deleting!"
                sys.exit(1)
        elif action == "tag_terminator":
        	terminator()
        elif action == "regions":
            list_regions()
        else:
            print "Unsupported action!"
            sys.exit(1)
else:
    parser.print_help()
