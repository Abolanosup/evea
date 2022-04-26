import aiohttp
import re
import json
from bs4 import BeautifulSoup
import asyncio

url_domain: str=""
user: str= ""
password: str= ""

files_filemanager: str = ""
itemid: str = ""

login_lock: bool = False
upload_tasks: int = 0

http_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36'}

session: aiohttp.ClientSession = aiohttp.ClientSession()

async def login():
    global url_domain, user, password, session, files_filemanager, itemid, login_lock
    
    while login_lock:
        print("Hay otro inicio de sesión en proceso. Esperando...")
        await asyncio.sleep(1)

    login_lock = True

    if await check_login():
        ret = True 
    else:
        print("Iniciando sesión en " + url_domain + " ...")
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with session.get(url=url_domain + "/login/index.php", headers=http_headers, timeout=timeout) as response:
                token = await response.text()

            pattern_auth = '<input type="hidden" name="logintoken" value="\w{32}">'
            token = re.findall(pattern_auth, token)
            token = re.findall("\w{32}", token[0])[0]
        
        
            payload = {'anchor': '', 'logintoken': token, 'username': user, 'password': password}
            
            async with session.post(url=url_domain + "/login/index.php", headers=http_headers, data=payload, timeout=timeout) as response:
                loginresponse = await response.text()
            
            if loginresponse.count("loginerrormessage"):
                print("Error de inicio de sesión. Datos incorrectos.")
                ret = False
            elif loginresponse.count("<title>"):
                print("Sesión iniciada.")
                ret = True
        except:
            print("Error de inicio de sesión. Error desconocido.")
            ret = False
    login_lock = False
    return ret


async def check_login():
    global url_domain, user, password, session
    print("Comprobando sesión...")
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with session.get(url=url_domain + "/my/", headers=http_headers, allow_redirects=False, timeout=timeout) as response:
            html = await response.text()

        if response.status == 200:
            print("Sesión activa.")
            return True
    except:
        pass

    print("No hay sesión")
    return False

async def upload(path, callback=None):
    global url_domain, files_filemanager, itemid, upload_tasks

    if upload_tasks == 0:
        files_filemanager = ""
        itemid = ""
    upload_tasks += 1

    try:
        up_session = session

        #Obtener parámetros
        timeout = aiohttp.ClientTimeout(total=10)
        async with up_session.get(url=url_domain + "/user/files.php?", headers=http_headers, timeout=timeout) as response:
            r_1 = await response.text()

        soup = BeautifulSoup(r_1,'html.parser')
        sesskey = soup.find('input',attrs={'name':'sesskey'})['value']
        query = extractUrlParams(soup.find('object',attrs={'type':'text/html'})['data'])

        client_id_pattern = '"client_id":"\w{13}"'
        client_id = re.findall(client_id_pattern, r_1)
        client_id = re.findall("\w{13}", client_id[0])[0]

        if itemid == "" : itemid = query['itemid']
        if files_filemanager == "" : files_filemanager = itemid

        print("Static itemid/filemanager: " + itemid + "/"  + files_filemanager)
        print("Tareas restantes: " + str(upload_tasks))

        _qf__user_files_form = soup.find('input',attrs={'name':'_qf__user_files_form'})['value']

        #Crear payloads POST
        data = aiohttp.FormData()
        data.add_field('title', '')
        data.add_field('author', 'Lucia')
        data.add_field('license', "allrightsreserved")
        data.add_field('itemid', itemid)
        data.add_field('repo_id', "4")
        data.add_field('p', '')
        data.add_field('page', '')
        data.add_field('env', query['env'])
        data.add_field('sesskey', sesskey)
        data.add_field('client_id', client_id)
        data.add_field('maxbytes', query['maxbytes'])
        data.add_field('areamaxbytes', query['areamaxbytes'])
        data.add_field('ctx_id', query['ctx_id'])
        data.add_field('savepath', '/')
        data.add_field('repo_upload_file', open(path, 'rb'))
        
        #Subir Archivo a DRAFTS
        print("Subiendo: " + path + " ...")

        timeout = aiohttp.ClientTimeout(total=60*60)
        async with up_session.post(url=url_domain + "/repository/repository_ajax.php?action=upload", data=data, headers=http_headers, timeout=timeout) as response:
            resp = await response.text()

        resp = json.loads(resp)
        print(resp)

        #No Guardar Cambios
        #if files_filemanager == "" : files_filemanager = soup.find('input',attrs={'name':'files_filemanager'})['value']

        payload = {
                'returnurl':url_domain + "/user/files.php",
                'sesskey':sesskey,
                '_qf__user_files_form':_qf__user_files_form,
                'files_filemanager':files_filemanager,
                'cancel':'Cancel'
               # 'submitbutton':'Guardar+cambios'
            }
            
        timeout = aiohttp.ClientTimeout(total=10)
        async with up_session.post(url=url_domain + "/user/files.php", data=payload, headers=http_headers, timeout=timeout) as response:
            await response.text()
    except:
        resp = {'error': 'Error. Error desconocido.'}

    upload_tasks -= 1
    return resp
    
        


def extractUrlParams(url):
        tokens = str(url).split('?')[1].split('&')
        retQuery = {}
        for q in tokens:
            qspl = q.split('=')
            retQuery[qspl[0]] = qspl[1]
        return retQuery
