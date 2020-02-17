import paramiko
from paramiko.ssh_exception import BadHostKeyException, AuthenticationException, SSHException, socket


# class SshShell:
#
#     def __init__(self, device):
#
#         self.server = device
#         self.ssh_connection = None
#         self.channel = None
#
#     def run_ssh_connection(self):
#
#         try:
#             self.ssh_connection = paramiko.SSHClient()
#             self.ssh_connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#             self.ssh_connection.connect(
#                 self.server[0],
#                 username=self.server[1],
#                 password=self.server[2],
#                 timeout=5,
#                 auth_timeout=5
#             )
#
#             self.channel = self.ssh_connection.invoke_shell()
#
#         except(BadHostKeyException, AuthenticationException, SSHException, socket.error) as e:
#             print(self.server[0] + ': ' + str(e))
#             return False
#
#         return True
#
#     def send_command(self, command):
#
#         try:
#             stdin, stdout, stderr = self.ssh_connection.exec_command(command)
#             output = stdout.read().splitlines()
#             prompt = []
#
#             for line in output:
#                 prompt.append(line.decode())
#
#         except (SSHException, EOFError) as e:
#             print(self.server[0] + ': ' + str(e))
#
#         return prompt
#
#     def disconnect(self):
#         self.ssh_connection.close()

# switch = ['10.10.1.200','a_ext_se_nxo_sdouill', 'Passw0rd2019-SPM']
# command = 'show running-config'
#
# conn = SshShell(switch)
#
# if conn.run_ssh_connection():
#     t_len = conn.send_command('terminal length 0')
#
#     hn = conn.send_command('show running-config | include hostname')
#     print(hn)
#
#     logs = conn.send_command('show logging | include %')
#     print(logs)
#
#     t_len = conn.send_command('no terminal length')
#     print(t_len)
#
# conn.disconnect()

# def run_ssh_connection_paramiko(server):
#     """Etablit une connexion SSH (paramiko)"""
#
#     try:
#         ssh_connection = paramiko.SSHClient()
#         ssh_connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         ssh_connection.connect(
#             server[0],
#             username=server[1],
#             password=server[2],
#             timeout=5,
#             auth_timeout=5
#         )
#
#     except(BadHostKeyException, AuthenticationException, SSHException, socket.error) as e:
#         print(server[0] + ': ' + str(e))
#         return False
#
#     return ssh_connection

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.1.150', username='a_ext_se_nxo_sdouill', password='Passw0rd2019-SPM', timeout=3, auth_timeout=3)

channel = client.invoke_shell()
stdin = channel.makefile('wb')

stdin.write('''
 copy running-config tftp://10.10.2.1/


 ''')

# switch = ['10.10.1.200','a_ext_se_nxo_sdouill', 'Passw0rd2019-SPM']
# conn = run_ssh_connection_paramiko(switch)
#
# if conn:
#     print('ok')
#     channel = conn.invoke_shell()
#     stdin = channel.makefile('wb')
#
#     stdin.write('''
#                  copy running-config tftp://10.10.2.1/
#
#
#                  exit
#                  ''')
#
#     print('ok2')
#     conn.close()