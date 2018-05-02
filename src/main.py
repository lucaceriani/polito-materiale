import os
from polito_web import PolitoWeb


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":

    sess = PolitoWeb()
    sess.set_dl_folder("C:\\materiale_polito")

    # esempio di user-agent che si può usare (non è obbligatorio)
    sess.set_user_agent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.75.14 (KHTML, like Gecko) \
    Version/11.1 Safari/7046A194A")

    print("PoliTo Materiale - v 0.0.3", end="\n\n")

    print("Credenziali di accesso per http://didattica.polito.it")
    while not sess.login():
        print("Impossibile effettuare il login, riprovare!")

    sess.get_lista_mat()
    while sess.menu():
        clear()
