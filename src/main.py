from polito_web import PolitoWeb

if __name__ == "__main__":

    # Creo la sessione.
    sess = PolitoWeb()

    # Imposto la cartella di download.
    sess.set_dl_folder("C:\\materiale_polito")

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
    sess.set_user_agent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.75.14 (KHTML, like Gecko) \
    Version/11.1 Safari/7046A194A")

    # Chiedo all'utente lo username e la password. Si possono anche
    # impostare di default chiamando al posto di sess.login()
    # sess.login('il_tuo_username', 'la_tua_password').
    sess.login()

    # Mostro il menù.
    sess.menu()
