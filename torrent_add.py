""" Add torrents to rTorrent """
import sys
import os
import argparse
import getpass
import ctypes
import keyring

from pyruTorrent.pyruTorrent  import rTorrent

VERBOSE = False
RT = None
MB_ICONEXCLAMATION = 0x30
MB_ERRORICON = 0x10

def vprint(data):
    """ Print data if verbose is enabled """
    if VERBOSE:
        print(data)

def msgbox (title, text, style=MB_ICONEXCLAMATION):
    """ Show a message box """
    response = ctypes.windll.user32.MessageBoxW(0, text, title, style)
    return response


def add_torrent(torrent_item):
    """ Add torrent to rTorrent and start it """
    torrent_ret = RT.add_torrent(
        torrent_item,
        download_path=None,
        label=None,
        ratio_group=None,
        add_stopped=False,
        add_name_to_path=True,
        save_uploaded_torrent=False
    )
    try:
        hash_t = torrent_ret[0].get('hash', None)
        if hash_t:
            vprint(f"Torrent added: {hash_t}")
            RT.start(hash_t)
    except Exception as e:
        vprint(f"Error adding torrent: {e}")


parser = argparse.ArgumentParser(description='Add torrents to rTorrent.')
parser.add_argument('--config', action='store_true', help='Start in config mode')
parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
parser.add_argument ('--set-rutorrent-path', dest="set_path", type=str, help='Set ruTorrent base path', default=None)
# Make 'torrent_file' optional by setting nargs='?' and default=None
parser.add_argument('torrent_file', type=str, nargs='?', default=None, help='Path to the torrent file')

args = parser.parse_args()
VERBOSE = args.verbose

if args.config:
    #print("Starting in config mode...")
    # Add your configuration mode logic here
    for i in [ "hostname", "username", "password", "rutorrent_path"]:
        if i == "password":
            keyring.set_password("torrent_add", i, getpass.getpass(f"Enter {i}: "))
        else:
            keyring.set_password("torrent_add", i, input(f"Enter {i}: "))
    sys.exit(0)

if args.set_path:
    keyring.set_password("torrent_add", "rutorrent_path", args.set_path)
    sys.exit(0)

rutorrent_basepath = keyring.get_password("torrent_add", "rutorrent_path")
if not rutorrent_basepath:
    rutorrent_basepath = "/rutorrent/"

if not all([keyring.get_password("torrent_add", i) for i in [ "hostname", "username", "password"]]):
    msgbox( "Error", "Error: Configuration not found. Run with --config to set up. Config doesn't work with the compiled version.")
    sys.exit(1)


if not args.torrent_file:
    msgbox("Error", "Error: No torrent file provided.")
    sys.exit(1)

RT = rTorrent(
	host=keyring.get_password("torrent_add", "hostname"),
	port=443,
	username=keyring.get_password("torrent_add", "username"),
	password=keyring.get_password("torrent_add", "password"),
	rpc_path=f'{rutorrent_basepath}plugins/httprpc/action.php'
)

try:
    if os.path.exists(args.torrent_file):
        add_torrent(args.torrent_file)
    else:
        msgbox("Error", f"Error: {args.torrent_file} does not exist.", MB_ERRORICON)
except Exception as e:
    msgbox("Error", f"Error: {e}", MB_ERRORICON)

#add_torrent(args[0])