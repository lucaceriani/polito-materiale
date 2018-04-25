import os
from polito_web import PolitoWeb

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__=="__main__":

    sess=PolitoWeb()
    sess.setDlFolder("C:\\materiale_polito")

    #esempio di user-agent che si può usare (non è obbligatorio)
    sess.setUserAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/11.1 Safari/7046A194A")

    print("PoliTo Materiale - v 0.0.2", end ="\n\n")

    print("Credenziali di accesso per http://didattica.polito.it")
    while not sess.login():
        print("Impossibile effettuare il login, riprovare!")

    sess.getListaMat()
    while sess.menu():
        clear()
