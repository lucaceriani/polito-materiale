import requests
import os
import re
import html
import getpass


class PolitoWeb:

    dl_folder = None
    login_cookie = None
    mat_cookie = None
    lista_mat = None
    working_folder = None
    last_time_udpated = None

    headers = {'User-Agent': 'python-requests'}
    base_url = 'https://didattica.polito.it/pls/portal30/'
    handler_url = base_url + 'sviluppo.filemgr.handler'
    get_process_url = base_url + 'sviluppo.filemgr.get_process_amount'
    file_last_update = 'last_update.txt'

    def set_user_agent(self, ua):
        self.headers['User-Agent'] = ua

    def set_dl_folder(self, dl_folder):
        # se la cartella non esiste la crea
        if not os.path.exists(dl_folder):
            os.makedirs(dl_folder)
        self.dl_folder = dl_folder

    def login(self, username=None, password=None):
        """
        :rtype: bool
        """
        if (username is None) and (password is None):
            user = input("Username: ")
            passw = getpass.getpass("Password: ")
        else:
            user = username
            passw = password

        print("Logging in...")

        with requests.session() as s:
            s.get('https://idp.polito.it/idp/x509mixed-login', headers=self.headers)
            r = s.post('https://idp.polito.it/idp/Authn/X509Mixed/UserPasswordLogin',
                       data={'j_username': user, 'j_password': passw}, headers=self.headers)
            rls = html.unescape(re.findall('name="RelayState".*value="(.*)"', r.text))
            if len(rls) > 0:
                relaystate = rls[0]
            else:
                return False
            samlresponse = html.unescape(re.findall('name="SAMLResponse".*value="(.*)"', r.text)[0])
            s.post('https://www.polito.it/Shibboleth.sso/SAML2/POST',
                   data={'RelayState': relaystate, 'SAMLResponse': samlresponse}, headers=self.headers)
            r = s.post('https://login.didattica.polito.it/secure/ShibLogin.php', headers=self.headers)
            relaystate = html.unescape(re.findall('name="RelayState".*value="(.*)"', r.text)[0])
            samlresponse = html.unescape(re.findall('name="SAMLResponse".*value="(.*)"', r.text)[0])
            r = s.post('https://login.didattica.polito.it/Shibboleth.sso/SAML2/POST',
                       data={'RelayState': relaystate, 'SAMLResponse': samlresponse}, headers=self.headers)
            if r.url == "https://didattica.polito.it/portal/page/portal/home/Studente":  # Login Successful
                login_cookie = s.cookies
            else:
                return False
        # se sono arrivato qui vuol dire che sono loggato
        self.login_cookie = login_cookie
        return True

    def get_lista_mat(self):
        # riceve la lista della materie sulla pagina principale del portale
        with requests.session() as s:
            s.cookies = self.login_cookie
            hp = s.get('https://didattica.polito.it/portal/page/portal/home/Studente', headers=self.headers)
            self.lista_mat = re.findall("cod_ins=(.+)&incarico=([0-9]+).+>(.+)[ ]*<", hp.text)

    def select_mat(self, indice):
        # seleziona la materia e imposta i cookie per la materia corrente in self.matCookie
        # inoltre crea al cartella per ospirate i file scaricati
        # voglio un nome cartella che sia fattibile: tolgo i caratteri non alfabetici
        nome_mat = self.purge_string(self.lista_mat[indice][2])
        cartella_da_creare = os.path.join(self.dl_folder, nome_mat)
        if not os.path.exists(cartella_da_creare):
            os.makedirs(cartella_da_creare)
        self.working_folder = cartella_da_creare

        with requests.session() as s:
            s.cookies = self.login_cookie
            s.get('https://didattica.polito.it/pls/portal30/sviluppo.chiama_materia',
                  params={'cod_ins': self.lista_mat[indice][0], 'incarico': self.lista_mat[indice][1]},
                  headers=self.headers)
            self.mat_cookie = s.cookies
            self.get_path_content(self.working_folder, '/')

    def get_path_content(self, cartella, path, code='0'):
        with requests.session() as s:
            s.cookies = self.mat_cookie
            # se non specifico il codice vuole dire che sono nella cartella iniziale e quindi
            # non devo inviare l'attributo code altrimenti mi esce un risultato non valido (??)
            if code != '0':
                json_result = s.get(self.handler_url, params={'action': 'list', 'path': path, 'code': code},
                                    headers=self.headers)
            else:
                json_result = s.get(self.handler_url, params={'action': 'list', 'path': path}, headers=self.headers)

            contenuto = json_result.json()

            # per controllare gli aggiornamenti mi serve il codice della cartella
            # lo prendo dal parent code del primo elemento che mi capita
            if path == '/':
                folder_code = contenuto['result'][0]['parent_code']
                ultimo_aggiornamento_remoto = self._last_update_remote(folder_code)
                if not self._need_to_update(cartella, folder_code):
                    print("Corso già aggiornato! (premi invio)")
                    input()
                    return

            for i in contenuto['result']:
                if i['type'] == 'dir':
                    if i['name'].startswith('ZZZZZ'):  # si tratta delle videolezioni
                        continue

                    # creo la cartella su cui procedere ricorsivamente
                    name = self.purge_string(i['name'])  # pulizia dei caratteri
                    cartella_da_creare = os.path.join(cartella, name)

                    if not os.path.exists(cartella_da_creare):
                        os.makedirs(cartella_da_creare)
                    print('Cartella: ' + name)
                    new_path = self.my_path_join(cartella_da_creare, name)
                    self.get_path_content(cartella_da_creare, new_path, i['code'])
                elif i['type'] == 'file':
                    # scarico i file
                    print('File: ' + i['nomefile'])
                    self.download_file(cartella, i['nomefile'], path, i['code'])

            if path == '/':
                # salvo l'ultimo aggiornamento remoto
                file_da_controllare = os.path.join(*[self.dl_folder, cartella, self.file_last_update])
                with open(file_da_controllare, 'w') as f:
                    return f.write(ultimo_aggiornamento_remoto)

    @staticmethod
    def my_path_join(a, b):
        if a.endswith('/'):
            return a + b
        else:
            return a + '/' + b

    @staticmethod
    def purge_string(a):
        return re.sub('[^a-zA-Z0-9 ]', '', a).strip()

    def download_file(self, cartella, name, path, code):
        with requests.session() as s:
            s.cookies = self.mat_cookie
            file = s.get(self.handler_url, params={'action': 'download', 'path': (path + '/' + name), 'code': code},
                         allow_redirects=True, headers=self.headers)
            open(os.path.join(cartella, name), 'wb').write(file.content)

    def menu(self):
        i = 1
        for mat in self.lista_mat:
            print('[%.2d] %s' % (i, mat[2]))
            i += 1
        x = -1
        while x not in range(1, i):
            x = int(input("Materia: "))
        self.select_mat(x-1)
        return True

    def _last_update_remote(self, folder_code):
        with requests.session() as s:
            s.cookies = self.mat_cookie
            json_result = s.get(self.get_process_url, params={'items': folder_code})
            if json_result:
                json_result = json_result.json()
                return json_result['result']['lastUpload']
            else:
                print("Impossibile stabilire la data dell'ultimo aggiornamento")
                return None

    def _last_update_local(self, cartella):
        file_da_controllare = os.path.join(*[self.dl_folder, cartella, self.file_last_update])
        if os.path.isfile(file_da_controllare):
            with open(file_da_controllare, 'r') as f:
                return f.read()
        else:
            return None

    def _need_to_update(self, cartella, folder_code):
        local = self._last_update_local(cartella)
        remote = self._last_update_remote(folder_code)
        if local is not None and remote is not None:
            if local < remote:
                return True
            else:
                return False
        else:
            return True  # se non trovo niente è come se dovessi aggiornare tutto
