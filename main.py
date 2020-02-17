import os
import csv
import collections

from queue import Queue
from utils import file_browser
from module_utils import cisco


class Home:

    def __init__(self):
        self.clear = lambda: os.system('cls')
        self.f_path = file_browser()

        if self.f_path:
            self.clear()
            self.options()

        else:
            exit()

    def run(self):
        switcher = {
            '1': cisco.RunSwitchesBackup,
            '2': cisco.GenerateLogReport,
            '3': self.run_topology
        }

        while True:
            print('')
            op = input('Selectionnez une option: ')

            # func = switcher.get(option, lambda: print('Option invalide!'))

            if op in switcher:
                option = switcher.get(op)

                with open(self.f_path, 'r') as file:
                    reader = csv.reader(file, delimiter=';')
                    thread_count = 4
                    q = Queue()

                    for i in range(thread_count):
                        th = option(queue=q, f_path=self.f_path)
                        th.daemon = True
                        th.start()

                    for sw in reader:
                        q.put(sw)

                    q.join()
                    self.options

            elif op == '4':
                self.stop()

            else:
                print('Option invalide!')

    def options(self):
        print('')
        print(' Fichier: ' + str(self.f_path))
        print('')
        print(' ******************************')
        print('')
        print(' Options:')
        print(' 1)  Lancer une sauvegarde de la configuration')
        print(' 2)  Générer un rapport des logs')
        print(' 3)  Générer une cartographie')
        print(' 4)  Exit')

    def stop(self):
        """Clear la console et stop l'outil"""

        self.clear()
        exit()

        if self.f_path:
            return func

        else:
            print('Veuillez sélectionner un fichier CSV avant d\'utiliser une option.')


if __name__ == "__main__":
    home = Home()
    home.run()

