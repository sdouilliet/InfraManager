import socket
import os

from netmiko import ConnectHandler
from netmiko.ssh_exception import *
from tkinter import Tk
from tkinter import filedialog


def file_browser():
    Tk().withdraw()
    f_path = filedialog.askopenfilename(filetypes=[('CSV files', '.csv')])

    if f_path and os.path.isfile(f_path):
        return f_path

    else:
        return False


def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)

    except AttributeError:

        try:
            socket.inet_aton(address)

        except socket.error:
            return False

        return address.count('.') == 3

    except socket.error:
        return False

    return True


def run_ssh_connection(address, username, password):
    """Etabli une connexion SSH vers un serveur"""

    try:
        ssh_connection = ConnectHandler(
            address,
            username=username,
            password=password,
            device_type='cisco_ios'
        )

    except (NetMikoTimeoutException, SSHException) as e:
        return str(e)

    return ssh_connection


def get_cisco_hostname(conn):

    hn = conn.send_command('show running-config | include hostname')
    hostname = str(hn.replace('hostname ', ''))

    return hostname

