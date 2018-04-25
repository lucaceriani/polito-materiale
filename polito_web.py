import requests
import os
import re
import html
import getpass
import json
import logging as log

log.basicConfig(level=100, filename='log.log', format='%(asctime)s - %(levelname)s: %(message)s')

class PolitoWeb:

    dlFolder = None
    loginCookie = None
    matCookie = None
    listaMat = None
    workingFolder = None

    headers = {'User-Agent': 'python-requests'}
    baseUrl = 'https://didattica.polito.it/pls/portal30/sviluppo.filemgr.handler'

    def __init__(self):
        log.debug("Creata sessione PolitoWeb")

    def setUserAgent(self, ua):
        self.headers['User-Agent'] = ua

    def setDlFolder(self, dlFolder):
        # se la cartella non esiste la crea
        if not os.path.exists(dlFolder):
            os.makedirs(dlFolder)
        self.dlFolder = dlFolder

    # @return boolean
    def login(self, username=None, password=None):
        if (username is None) and (password is None):
            user=input("Username: ")
            passw=getpass.getpass("Password: ")
        else:
            user=username
            passw=password

        print("Logging in...")

        with requests.session() as s:
            r=s.get('https://idp.polito.it/idp/x509mixed-login', headers=self.headers)
            r=s.post('https://idp.polito.it/idp/Authn/X509Mixed/UserPasswordLogin', data={'j_username':user,'j_password':passw}, headers=self.headers)
            rls=html.unescape(re.findall('name="RelayState".*value="(.*)"',r.text))
            if len(rls)>0:
                relaystate=rls[0]
            else:
                log.error("Credenziali errate! Utente: %s", user)
                return False
            samlresponse=html.unescape(re.findall('name="SAMLResponse".*value="(.*)"',r.text)[0])
            r=s.post('https://www.polito.it/Shibboleth.sso/SAML2/POST', data={'RelayState':relaystate,'SAMLResponse':samlresponse}, headers=self.headers)
            r=s.post('https://login.didattica.polito.it/secure/ShibLogin.php', headers=self.headers)
            relaystate=html.unescape(re.findall('name="RelayState".*value="(.*)"',r.text)[0])
            samlresponse=html.unescape(re.findall('name="SAMLResponse".*value="(.*)"',r.text)[0])
            r=s.post('https://login.didattica.polito.it/Shibboleth.sso/SAML2/POST', data={'RelayState':relaystate,'SAMLResponse':samlresponse}, headers=self.headers)
            if r.url=="https://didattica.polito.it/portal/page/portal/home/Studente": #Login Successful
                login_cookie=s.cookies
            else:
                log.critical("Qualcosa nel login non ha funzionato!")
                return False
        # se sono arrivato qui vuol dire che sono loggato
        self.loginCookie=login_cookie
        return True

    def getListaMat(self):
        # riceve la lista della materie sulla pagina principale del portale
        with requests.session() as s:
            s.cookies = self.loginCookie
            hp = s.get('https://didattica.polito.it/portal/page/portal/home/Studente', headers=self.headers)
            self.listaMat = re.findall("cod_ins=(.+)&incarico=([0-9]+).+>(.+)[ ]*<", hp.text)

    def selectMat(self, id):
        # seleziona la materia e imposta i cookie per la materia corrente in self.matCookie
        # inoltre crea al cartella per ospirate i file scaricati
        # voglio un nome cartella che sia fattibile: tolgo i caratteri non alfabetici
        nomeMat = (re.sub(r'([^\s\w]|_)+', '', self.listaMat[id][2])).strip()
        cartellaDaCreare = os.path.join(self.dlFolder, nomeMat)
        if not os.path.exists(cartellaDaCreare):
            os.makedirs(cartellaDaCreare)
        self.workingFolder = cartellaDaCreare

        with requests.session() as s:
            s.cookies = self.loginCookie
            s.get('https://didattica.polito.it/pls/portal30/sviluppo.chiama_materia',
                   params={'cod_ins': self.listaMat[id][0], 'incarico': self.listaMat[id][1]},
                   headers=self.headers)
            self.matCookie = s.cookies
            self.getPathContent(self.workingFolder, '/')

    def getPathContent(self, cartella, path, code='0'):
        with requests.session() as s:
            s.cookies = self.matCookie
            # se non specifico il codice vuole dire che sono nella cartella iniziale e quindi
            # non devo inviare l'attributo code altrimenti mi esce un risultato non valido (??)
            if code != '0':
                json_result = s.get(self.baseUrl, params={'action': 'list', 'path': path, 'code': code}, headers=self.headers)
            else:
                json_result = s.get(self.baseUrl, params={'action': 'list', 'path': path}, headers=self.headers)

            contenuto = json_result.json()

            for i in contenuto['result']:
                if i['type'] == 'dir':
                    if i['name'].startswith('ZZZZZ'): continue # si tratta delle videolezioni
                    # creo la cartella su cui procedere ricorsivamente
                    cartellaDaCreare = os.path.join(cartella, i['name'])
                    if not os.path.exists(cartellaDaCreare):
                        os.makedirs(cartellaDaCreare)
                    print('Cartella: ' + i['name'])
                    newPath =  self.myPathJoin(cartellaDaCreare, i['name'])
                    self.getPathContent(cartellaDaCreare, newPath, i['code'])
                elif i['type'] == 'file':
                    # scarico i file
                    print('File: ' + i['nomefile'])
                    self.downloadFile(cartella, i['nomefile'], path, i['code'])

    def myPathJoin(self, a, b):
        if a.endswith('/'):
            return a + b
        else:
            return a + '/' + b

    def downloadFile(self, cartella, name, path, code):
        with requests.session() as s:
            s.cookies = self.matCookie
            file = s.get(self.baseUrl, params={'action':'download', 'path': (path + '/' + name), 'code': code}, allow_redirects=True, headers=self.headers)
            open(os.path.join(cartella, name), 'wb').write(file.content)

    def menu(self):
        i=1
        for mat in self.listaMat:
            print('[%.2d] %s' % (i, mat[2]))
            i+=1
        x=-1
        while x not in range(1,i):
            x=int(input("Materia: "))
        self.selectMat(x-1)
        os.system("pause")
        return True
