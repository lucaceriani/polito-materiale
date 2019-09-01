import os
import sys

from polito_web import PolitoWeb

if __name__ == "__main__":

    # Creo la sessione.
    print("PoliTo Materiale - v 1.1.2", end="\n")
    sess = PolitoWeb()

    # Imposto la cartella di download di default
    home = os.path.expanduser('~')
    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        sess.set_dl_folder(home + "/polito-materiale")
    elif sys.platform.startswith('win'):
        sess.set_dl_folder(home + "\\polito-materiale")

    # Togliere il commento dalla riga seguente e modificarlo nel caso si volesse settare
    # una cartella per il download diversa da quella di default
    # sess.set_dl_folder("Path/Che/Desidero")

    # Imposto che il nome dei file sia quello che appare
    # sul sito e non quello effettivo del file. Ad esempio
    # sul sito esiste il file "Esercizio 1.pdf", quando lo si
    # scarica diventa "es_1.pdf". Scegliendo l'opzione 'web'
    # si mantiene il nome che compare sul sito, scegliendo
    # l'opzione 'nomefile' si usa il vero nome del file.
    sess.set_nome_file('web')

    # Imposto lo user agent. Si tratta di una stringa che indica che tipo
    # di browser e sistema operativo state usando, potete anche omettere questo
    # settaggio. In questo esempio si usa Safari su OSX.
    sess.set_user_agent("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0")

    # Chiedo all'utente lo username e la password.
    sess.login()

    # Mostro il menù.
    sess.menu()
