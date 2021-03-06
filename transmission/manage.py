#!/usr/bin/python

import sys
import shlex
import subprocess
import argparse
import urllib

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'

app_name = 'transmission'

parser = argparse.ArgumentParser(description='Manage %s container' % app_name, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("execute", choices=['create','start','stop','restart','delete'], help='manage %s server' % app_name)
parser.add_argument("-d", "--downloads", type=str, default="", help="path to downloads directory")
parser.add_argument("-t", "--torrents", type=str, default="", help="path to torrents-to-watch directory")
parser.add_argument("-u", "--username", type=str, default="guest", help="transmission rpc-username")
parser.add_argument("-p", "--password", type=str, default="guest", help="transmission rpc-password")
parser.add_argument("--whitelist", type=str, default="*.*.*.*", help="transmission rpc-whitelist")
parser.add_argument("--rss_feed", type=str, default="", help="PT rss feed address")
args = parser.parse_args()

cmd_dict = { \
	"create" : \
		"docker run --net=host " \
		"-e T_user={1} -e T_passwd={2} -e T_whitelist={3} -e T_rss={4} " \
		"-v {5}:/var/lib/transmission-daemon/downloads " \
		"-v {6}:/var/lib/transmission-daemon/torrents " \
		"--name {0} -d catatnight/{0}" \
		.format(app_name, args.username, args.password, args.whitelist, args.rss_feed, args.downloads, args.torrents), \
   "start"  : "docker start   %s" % app_name, \
   "stop"   : "docker stop    %s" % app_name, \
   "restart": "docker restart %s" % app_name, \
   "delete" : "docker rm -f   %s" % app_name}
cmd_key = args.execute
if cmd_key == 'create' and (args.downloads == '' or args.torrents == ''):
	sys.exit(bcolors.WARNING + "Error: Paths to downloads and torrents must be set. " + bcolors.ENDC)

process = subprocess.Popen(shlex.split(cmd_dict[cmd_key]), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if process.stdout.readline():
	print bcolors.OKGREEN + cmd_key + " %s successfully" % app_name + bcolors.ENDC
	if cmd_key == 'create':
		ip = urllib.urlopen('http://icanhazip.com/').read().strip()
		print bcolors.OKGREEN + \
			"You can visit web client on http://{0}:9091 with username/password:{1}/{2}".format(ip, args.username, args.password) \
			+ bcolors.ENDC
else:
	stderr = process.stderr.readline()
	if 'No such container' in stderr:
		print bcolors.WARNING + "Please create %s container first" % app_name + bcolors.ENDC
	else:
		print bcolors.WARNING + stderr + bcolors.ENDC
output = process.communicate()[0]
