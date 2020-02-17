import os
import threading
import webbrowser
import time
import netmiko

from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from utils import *


class RunSwitchesBackup(threading.Thread):
    """Récupére la running-config des switches et l'enregistre dans dans un fichier local"""

    def __init__(self, queue):
        threading.Thread.__init__(self)

        self.queue = queue

    def run(self):
        """Sauvegarde des switches"""

        while True:
            switch = self.queue.get()

            sw_address = switch[0]
            sw_username = switch[1]
            sw_password = switch[2]

            print('Sauvegarde du switch ' + sw_address + '.')
            conn = run_ssh_connection(address=sw_address, username=sw_username, password=sw_password)

            if type(conn) is netmiko.cisco.cisco_ios.CiscoIosSSH:
                sw_hostname = get_cisco_hostname(conn)

                show_run = conn.send_command('show running-config')
                run_config = show_run.split('\n', 3)[3];

                file = open('backup/' + sw_hostname, 'w')
                file.write(run_config)
                file.close()

                conn.disconnect()

            else:
                print(conn)

            # Arrêt de la boucle une fois la queue vide
            self.queue.task_done()


class GenerateLogReport(threading.Thread):
    """Génére un rapport sur les journaux d'une liste de switches"""

    def __init__(self, queue):
        threading.Thread.__init__(self)

        self.queue = queue
        self.content = ''

    def run(self):

        while True:
            switch = self.queue.get()

            sw_address = switch[0]
            sw_username = switch[1]
            sw_password = switch[2]

            print('Traitement du switch ' + sw_address + '.')
            conn = run_ssh_connection(address=sw_address, username=sw_username, password=sw_password)

            if type(conn) is netmiko.cisco.cisco_ios.CiscoIosSSH:
                conn.send_command('terminal length 0')

                # Récupération du hostname du switch
                sw_hostname = get_cisco_hostname(conn)

                # Collecte des logs
                prompt = conn.send_command('show logging | include %')

                conn.send_command('no terminal length')

                # Fermeture de la session
                conn.disconnect()

                # Triage des logs dans un tableau
                logs = self.parse(prompt)

                # Génération d'un rapport HTML à partir du tableau
                self.convert_to_html(sw_hostname, sw_address, logs)

            else:
                print(conn)
                self.content += '<h2 class="error">' + conn + '</h2>'

            # Arrêt de la boucle une fois la queue vide
            self.queue.task_done()

    def parse(self, logs_prompt):
        """Trie les messages de logs par niveau et les enregistre dans l'attribut self.log_table"""

        log_table = [[], [], [], [], [], [], [], []]
        logs = logs_prompt.split('\n')

        for line in logs:
            # Recherche la position du caractère "%"
            facility_position = line.find('%')

            # Recherche la position du premier "-" à partir de la position de "%"
            dash_position = line.find('-', facility_position)

            # Recupération du caractère suivant le "-"
            severity_position = dash_position + 1
            severity_tmp = line[severity_position:severity_position + 1]

            # Vérification du caractère récupéré
            while True:
                # Si le caractère est un chiffre, alors il correspond au niveau de sévérité du message de log
                if severity_tmp.isdigit():
                    severity = int(severity_tmp)
                    log_table[severity].append(line.strip())  # on stock le message selon son niveau
                    break

                # Sinon on recherche la position du caractère "-" suivant
                else:
                    next_dash_position = line.find('-', severity_position)

                    # Si un "-" est trouvé à partir du "-" précédent, on récupére le caractère suivant le "-"
                    if not facility_position == -1:
                        next_severity_position = next_dash_position + 1  # on suppose la position du severity
                        # on extrait le caractère
                        severity_tmp = line[next_severity_position:next_severity_position + 1]

                    # Sinon la boucle s'arrête et l'on passe à la ligne suivante
                    else:
                        break

        return log_table

    def convert_to_html(self, sw_hostname, sw_ip, logs):
        """Trie et ajout les logs d'un switch dans le content du rapport HTML"""

        i = 0
        report_switch = ''

        for lvl in logs:  # Pour chaque liste dans dans la table des logs

            # Définition le titre du niveau selon le niveau de la liste
            report_switch += '<h3>Level ' + str(i) + ' message</h3>'

            if len(lvl) > 0:  # Si la liste n'est pas vide
                report_switch += '<div class="code">'  # on ouvre un div au rapport

                for message in lvl:  # Pour chaque message dans la liste
                    report_switch += message + '<br />'  # on l'ajout dans report_switch

                report_switch += '</div>'  # on ferme le div
            else:  # Sinon on stock No message.
                report_switch += '<p class="nomsg">No message.</p>'

            i = i + 1

        # Définition du titre
        title = '<h2 id="' + sw_hostname + '" class="connected">' + sw_hostname + ' (' + sw_ip + ')</h2>'

        # Chargement du répertoire des templates html
        t_folder = FileSystemLoader('templates')
        # Création de l'environnement
        environment = Environment(loader=t_folder)

        # Chargement du template report_switch_template.html
        template = environment.get_template('report_switch_template.html')

        # Ajout du rapport dans content
        self.content += template.render(title=title, switch_name=sw_hostname, report_switch=report_switch)

    def generate_report(self):
        """Génére le rapport final"""

        file_loader = FileSystemLoader('templates')  # Chargement du répertoire des templates html
        env = Environment(loader=file_loader)  # Création de l'environnement

        # Chargement du template report_template.html
        template = env.get_template('report_template.html')

        # Récupération de la date et de l'heure
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        # Génération du contenu rapport HTML
        output = template.render(datenow=dt_string, report=self.content)

        dt_file = now.strftime("%d-%m-%Y à %H-%M-%S")
        report_name = 'rapport du ' + dt_file + '.html'

        # Création du rapport
        report_file = open(report_name, 'w')
        report_file.write(output)
        report_file.close()

        # Ouverture du rapport dans le navigateur par défaut
        webbrowser.open_new_tab(report_name)


class GenerateTopology(threading.Thread):

    def __init__(self, queue, user, pawd):
        threading.Thread.__init__(self)

        self.queue = queue

    def run(self):

        while True:
            hostname = self.queue.get()
            print('Analyse de ' + hostname)
            conn = self.connection(hostname)

            if conn is not False:
                device_name = self.get_hostname(conn)
                devices_list = self.get_neighbors_ids(conn)
                ifaces_list = self.get_interfaces(conn)

                neighbors = {}
                for n in devices_list:
                    interco = ifaces_list[devices_list.index(n)].split(',')

                    neighbors.update(
                        {
                            n: {
                                'Lport': interco[0],
                                'Rport': interco[1]
                            }
                        }
                    )

                global_cdp_neighbors.append(
                    {
                        device_name: neighbors
                    }
                )

            self.queue.task_done()

        conn.disconnect()

    def connection(self, hostname):

        try:
            ssh_connection = ConnectHandler(
                hostname,
                username=self.username,
                password=self.password,
                device_type='cisco_ios'
            )

        except (NetMikoTimeoutException, SSHException) as e:
            print('Erreur: ' + str(e))
            return False

        return ssh_connection

    @staticmethod
    def get_hostname(conn):
        show_run_hn = conn.send_command('show running-config | include hostname')
        hostname = str(show_run_hn.replace('hostname ', ''))

        return hostname

    @staticmethod
    def get_neighbors_ids(conn):
        show_devices_ids = conn.send_command('show cdp neighbors detail | include Device ID:')
        string1 = str(show_devices_ids.replace('Device ID: ', ''))
        devices_list = string1.split('\n')

        return devices_list

    @staticmethod
    def get_interfaces(conn):
        show_interfaces = conn.send_command('show cdp neighbors detail | include Interface:')
        string1 = str(show_interfaces.replace('Interface: ', ''))
        string2 = str(string1.replace('  Port ID (outgoing port): ', ''))
        iface_list = string2.split('\n')

        return iface_list