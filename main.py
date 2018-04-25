import os
from polito_web import PolitoWeb

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__=="__main__":

    sess=PolitoWeb()
    sess.setDlFolder("C:\\materiale_polito")

    print("PoliTo Materiale - v 0.0.1", end ="\n\n")

    print("Credenziali di accesso per http://didattica.polito.it")
    while not sess.login():
        print("Impossibile effettuare il login, riprovare!")

    sess.getListaMat()
    while sess.menu():
        clear()
