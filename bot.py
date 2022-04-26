from logging import exception
import multiFile 
import zipfile
from zipfile import ZipFile
import Config
import json
from Config import Config
import time
import random
import requests
import json
from mega import Mega
from os import popen
from bs4 import BeautifulSoup
from aiohttp.client import ClientSession
import telethon as O
from telethon import TelegramClient, events, sync
from telethon.events import NewMessage as J,CallbackQuery as P,newmessage
from telethon.tl.custom import Message,Button as Q,message
from telethon.tl.types import User
import asyncio as R
from functools import partial as S
from datetime import datetime as K,timezone as L,timedelta as T
import re,os,base64,moodle_client as B,strings as A
from comfig import*

proces_file = b'FILE_Dowload'
proces_url = b'FILE_URL_Dowload'
proces_megaurl = b'File_Mega_Down'
Config = Config()
m = Mega()

C=str.maketrans('1357926840NOEQRSTUVWXYZnopqrstuvwxyzABCDPFGHIJKLMabcdefghijklm','ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz1234567890')

def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)

def req_file_size(req):
    try:
        return int(req.headers['content-length'])
    except:
        return 0

def get_url_file_name(url,req):
    try:
        if "Content-Disposition" in req.headers.keys():
            return str(re.findall("filename=(.+)", req.headers["Content-Disposition"])[0])
        else:
            tokens = str(url).split('/');
            return tokens[len(tokens)-1]
    except:
           tokens = str(url).split('/');
           return tokens[len(tokens)-1]
    return ''

def get_name(file):
    return str(file)

def fixed_name(name):
    return str(name).replace('%20',' ')

def U(secs):
	def A(f):
		B='last_update'
		A={B:K.now(L.utc)}
		async def C(*D,**E):
			C=K.now(L.utc)
			if C-A[B]<T(seconds=secs):
				return
			A[B]=C
			return await f(*D,**E)
		return C
	return A

async def M(message):
	A=message
	try:
		B = get_name(A.file.name)
		C = sizeof_fmt(A.file.size)
	except Exception as i:
		print(str(i))
	return B,C

def mediafire(url: str) -> str:
    """ MediaFire direct links generator """
    try:
        link = re.findall(r'\bhttps?://.*mediafire\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No MediaFire links found\n")
    page = BeautifulSoup(requests.get(link).content, 'lxml')
    info = page.find('a', {'aria-label': 'Download file'})
    return info.get('href')

def gdrive(url: str) -> str:
    """ GDrive direct links generator """
    drive = "https://drive.google.com"
    try:
        link = re.findall(r"\bhttps?://drive\.google\.com\S+", url)[0]
    except IndexError:
        reply = "`No Google drive links found`\n"
        return reply
    file_id = ""
    reply = ""
    if link.find("view") != -1:
        file_id = link.split("/")[-2]
    elif link.find("open?id=") != -1:
        file_id = link.split("open?id=")[1].strip()
    elif link.find("uc?id=") != -1:
        file_id = link.split("uc?id=")[1].strip()
    url = f"{drive}/uc?export=download&id={file_id}"
    download = requests.get(url, stream=True, allow_redirects=False)
    cookies = download.cookies
    try:
        # In case of small file size, Google downloads directly
        dl_url = download.headers["location"]
        if "accounts.google.com" in dl_url:  # non-public file
            reply += "`Link is not public!`\n"
            return reply
        name = 'Direct Download Link'
    except KeyError:
        # In case of download warning page
        page = BeautifulSoup(download.content, "lxml")
        export = drive + page.find("a", {"id": "uc-download-link"}).get("href")
        name = page.find("span", {"class": "uc-name-size"}).text
        response = requests.get(
            export, stream=True, allow_redirects=False, cookies=cookies
        )
        dl_url = response.headers["location"]
        if "accounts.google.com" in dl_url:
            reply += "Link is not public!"
            return reply
    return dl_url

async def down_list(ev, msg, bot, url):
	    try:
                req = requests.get(url, stream = True,allow_redirects=True)
                file_size = req_file_size(req)
                Config.descargado += int(file_size)
                chunk_size = 1024 * 1024 * Config.ChunkSize
                if req.status_code == 200:
                    file_name = get_url_file_name(url,req)
                    file_name = file_name.replace('"',"")
                    file_name = fixed_name(file_name)
                    iterator = 1
                    file_wr = open(file_name,'wb')
                    print('Descargando...')
                    chunkpor = 0
                    chunkrandom = random.randint(10.00,30.00)
                    inicio = time.time()
                    total = file_size
                    for chunk in req.iter_content(chunk_size = 1024 * 1024 * chunkrandom):
                        if chunk:
                            chunkpor += len(chunk)
                            porcent = round(float(chunkpor / total * 100), 2)
                            make_text = str(porcent) + '% / 100%'
                            index_make = 1
                            make_text += '\n['
                            while(index_make<21):
                                if porcent >= index_make * 5:
                                    make_text+='█'
                                else: 
                                    make_text+='░'
                                index_make+=1
                            make_text += ']'
                            fin = time.time()
                            tiempo = round(float(fin-inicio), 2)
                            speed = round(float(len(chunk) / tiempo) / 1024 / 1024, 2)
                            inicio = 0
                            inicio = time.time()
                            await msg.edit('Descargando '+str(file_name)+'...\nProgreso:\n'+str(make_text)+'\nVelocidad: ' +str(float(speed))+'Mb/s\nDescargado: '+str(round(float(chunkpor) / 1024 / 1024, 2))+' MB\nTotal: ' +str(round(total / 1024 / 1024, 2))+ ' MB',buttons=None)
                            file_wr.write(chunk)
                    file_wr.close()
                    if file_size > chunk_size: 
                        if Config.up_zip == False:
                            multiFile.files.clear()
                        await msg.edit('Comprimiendo \n' + str(file_name) + '\n' + str(sizeof_fmt(file_size)),buttons=None)
                        mult_file =  multiFile.MultiFile(file_name+'.7z',chunk_size)
                        zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
                        zip.write(file_name)
                        zip.close()
                        mult_file.close()
                        i = 0
                        if Config.up_zip == True:
                            await msg.edit('Partes de {} agregadas a la cola'.format(file_name),buttons=None)
                            return
                        for f in multiFile.files:
                            await msg.edit(A.STR_SUBIENDO.format(str(f)),buttons=None)
                            Config.subiendo = 'Si'
                            Config.up_zip = True
                            if await B.login():
                                try:
                                    J = await B.upload(f)
                                    if J.get('event')=='fileexists':
                                        J=J.get('newfile')
                                    J = J['url']
                                    J = f + ':\n' + J.replace('\\','').replace('//','').replace(':','://') + '\n'
                                    await D.send_message(ev.chat_id, J)
                                    os.unlink(f)
                                except Exception as u:				
                                    await msg.edit(A.STR_ERROR + str(u),buttons=None)
                                    print(u)
                            else:
                                await msg.edit(A.STR_ERROR,buttons=None)
                            Config.subiendo = 'No'
                            Config.up_zip = False
                            await msg.edit('Proceso Finalizado!',buttons=None)
                    else:
                        await msg.edit(A.STR_SUBIENDO.format(str(file_name)),buttons=None)
                        Config.subiendo = 'Si'
                        if await B.login():
                            try:
                                U=await B.upload(file_name)
                                if U.get('event')=='fileexists':
                                    U=U.get('newfile')
                                U = U['url']
                                U = file_name+':\n'+U.replace('\\','').replace('//','').replace(':','://') + '\n'
                                await msg.edit('Proceso Finalizado!\n'+str(U),buttons=None)
                            except Exception as k:				
                                await msg.edit(A.STR_ERROR + str(k),buttons=None)
                        else:
                            await msg.edit(A.STR_ERROR,buttons=None)
                    Config.subiendo = 'No'
	    except Exception as j:
                Config.comprimiendo = False
                print(str(j))
	    return await help_down_list(ev, bot, url)

async def help_down_list(ev, bot, url):
	    try:
                Config.links.remove(url)
                if Config.links == []:
                    return
                else:
                    msg = await bot.send_message(ev.chat_id, 'Procesando siguiente link...')
                    url = Config.links[0]
                    return await down_list(ev, msg, bot, url)
	    except Exception as f:print(f)

if __name__=='__main__':
	try:
		H= (API_ID)
		V= (API_HASH)
		W= (BOT_TOKEN)
		E= (ADMIN_ID)
		B.user= Config.user
		B.password= Config.password
		B.url_domain= (MOODLE_URL)
		H=int(H)
		
	except Exception as e:
		print('Fallo en configuración.')
		raise Exception('Fallo en configuración.\n' +str(e))
	print('Iniciando bot...')
	D=O.TelegramClient('bot',api_id=int(H),api_hash=V).start(bot_token=W)
	D.send_message(E[0], 'Bot Activo :)')

	@D.on(J())
	async def NewMessage(event):
		Message=event.message
		if not int(event.message.sender_id)in E:
                    return
		if Message.file:
                    F,G=await M(Message)
                    H=await event.reply(A.STR_INFO_ARCHIVO.format(F,G),buttons=[[Q.inline('Descargar y Subir', proces_file)]])
                    await B.login()
		if Message.text:
                    if '/start' in Message.text:
                        B=event
                        C=await B.get_sender()
                        await D.send_message(B.chat_id,A.STR_WELCOME.format(C.first_name))
                        return
                    if '/status' in Message.text:
                        return await event.reply('Estado:\nTotal descargado:{}\nEn uso:{}'.format(sizeof_fmt(Config.descargado),str(Config.subiendo)),buttons=None)
                    if '/gc' in Message.text:
                        return await D.send_message(event.chat_id, 'El Tamaño de Los zip es '+str(Config.ChunkSize)+'\n\nUsuario: '+str(Config.user)+'\nPassword: '+str(Config.password))
                    if '/sc' in Message.text:
                        ev = event
                        text = ev.message.text
                        Config.setChunkSize(int(text.replace('/sc ','')))
                        return await D.send_message(ev.chat_id, 'Tamaño de Los zip Cambiado')
                    if '/add ' in Message.text:
                        ev = event
                        url = ev.message.text.replace('/add ','')
                        if 'drive.google.com' in url:
                            url = gdrive(url)
                            print(url)
                        elif 'mediafire' in url:
                            url = mediafire(url)
                        Config.links.append(str(url))
                        await ev.reply('Enlace agregado a la lista!\nConsultar lista: /list\nComenzar a descargar: /download_start')
                        return
                    if '/list' in Message.text:
                        links = str(Config.links).replace('[','').replace(']','').replace("'","```").replace(',','\n\n')
                        if Config.links == []:
                            return await event.reply('No hay ningún link en la lista')
                        return await event.reply('Lista de links:\n{}'.format(str(links)))
                    if '/download_start' in Message.text:
                        msg = await event.reply('Procesando...')
                        url = Config.links[0]
                        await down_list(event, msg, D, url)
                        await D.send_message(event.chat_id, 'Proceso Finalizado!!')
                        return
                    if 'http' in Message.text:
                        ev = event
                        url = ev.message.text
                        file_name = None
                        file_size = None
                        if 'drive.google.com' in url:
                            url = gdrive(url)
                            print(url)
                        elif 'mediafire' in url:
                            url = mediafire(url)
                        else: pass
                        print(url)
                        Config.url = ''
                        Config.url = url
                        req = requests.get(url, stream = True,allow_redirects=True)
                        if file_name == None:
                            file_name = get_url_file_name(url,req)
                            file_name = file_name.replace('"',"")
                            file_name = fixed_name(file_name)
                        if file_size == None:
                            file_size = req_file_size(req)
                        H = await ev.reply(A.STR_INFO_ARCHIVO.format(file_name,sizeof_fmt(file_size)),buttons=[[Q.inline('📥Descargar📥', proces_url)]])
                        return

	@D.on(P(data=re.compile(proces_url)))
	async def dtd(event):
	    ev = event
	    C = await ev.get_message()
	    I = await C.get_reply_message()
	    msg = C
	    url = Config.url
	    try:
                req = requests.get(url, stream = True,allow_redirects=True)
                file_size = req_file_size(req)
                Config.descargado += int(file_size)
                chunk_size = 1024 * 1024 * Config.ChunkSize
                if req.status_code == 200:
                    file_name = get_url_file_name(url,req)
                    file_name = file_name.replace('"',"")
                    file_name = fixed_name(file_name)
                    iterator = 1
                    file_wr = open(file_name,'wb')
                    print('Descargando...')
                    chunkpor = 0
                    chunkrandom = random.randint(10.00,30.00)
                    inicio = time.time()
                    total = file_size
                    for chunk in req.iter_content(chunk_size = 1024 * 1024 * chunkrandom):
                        if chunk:
                            chunkpor += len(chunk)
                            porcent = round(float(chunkpor / total * 100), 2)
                            make_text = str(porcent) + '% / 100%'
                            index_make = 1
                            make_text += '\n['
                            while(index_make<21):
                                if porcent >= index_make * 5:
                                    make_text+='█'
                                else: 
                                    make_text+='░'
                                index_make+=1
                            make_text += ']'
                            fin = time.time()
                            tiempo = round(float(fin-inicio), 2)
                            speed = round(float(len(chunk) / tiempo) / 1024 / 1024, 2)
                            inicio = 0
                            inicio = time.time()
                            await msg.edit('Descargando '+str(file_name)+'...\nProgreso:\n'+str(make_text)+'\nVelocidad: ' +str(float(speed))+'Mb/s\nDescargado: '+str(round(float(chunkpor) / 1024 / 1024, 2))+' MB\nTotal: ' +str(round(total / 1024 / 1024, 2))+ ' MB',buttons=None)
                            file_wr.write(chunk)
                    file_wr.close()
                    if file_size > chunk_size: 
                        if Config.up_zip == False:
                            multiFile.files.clear()
                        await msg.edit('Comprimiendo \n' + str(file_name) + '\n' + str(sizeof_fmt(file_size)),buttons=None)
                        mult_file =  multiFile.MultiFile(file_name+'.7z',chunk_size)
                        zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
                        zip.write(file_name)
                        zip.close()
                        mult_file.close()
                        i = 0
                        if Config.up_zip == True:
                            await C.edit('Partes de {} agregadas a la cola'.format(file_name),buttons=None)
                            return
                        for f in multiFile.files:
                            await C.edit(A.STR_SUBIENDO.format(str(f)),buttons=None)
                            Config.subiendo = 'Si'
                            Config.up_zip = True
                            if await B.login():
                                try:
                                    J = await B.upload(f)
                                    if J.get('event')=='fileexists':
                                        J=J.get('newfile')
                                    J = J['url']
                                    J = f + ':\n' + J.replace('\\','').replace('//','').replace(':','://') + '\n'
                                    await D.send_message(ev.chat_id, J)
                                    os.unlink(f)
                                except Exception as u:				
                                    await C.edit(A.STR_ERROR + str(u),buttons=None)
                                    print(u)
                            else:
                                await C.edit(A.STR_ERROR,buttons=None)
                            Config.subiendo = 'No'
                            Config.up_zip = False
                            await C.edit('Proceso Finalizado!',buttons=None)
                    else:
                        await C.edit(A.STR_SUBIENDO.format(str(file_name)),buttons=None)
                        Config.subiendo = 'Si'
                        if await B.login():
                            try:
                                U=await B.upload(file_name)
                                if U.get('event')=='fileexists':
                                    U=U.get('newfile')
                                U = U['url']
                                U = file_name+':\n'+U.replace('\\','').replace('//','').replace(':','://') + '\n'
                                await C.edit('Proceso Finalizado!\n'+str(U),buttons=None)
                            except Exception as k:				
                                await C.edit(A.STR_ERROR + str(k),buttons=None)
                        else:
                            await C.edit(A.STR_ERROR,buttons=None)
                    Config.subiendo = 'No'
                    
	    except Exception as j:
                Config.comprimiendo = False
                print(str(j))
	    if B.upload_tasks==0:
	        await D.send_message(ev.chat_id,A.STR_IDLE)

	@D.on(P(data=re.compile(proces_file)))
	async def d(event):
                J='./'
                E = ''
                U = ''
                H=event
                C=await H.get_message()
                I=await C.get_reply_message()
                Config.descargado += int(I.file.size)
                G,K=await M(I)
                await C.edit(A.STR_WAIT,buttons=None)
                L=await I.download_media(file=J+G,progress_callback=S(X,C,G))
                file = L
                file_size = I.file.size
                chunk_size = 1024 * 1024 * Config.ChunkSize
                if file_size > chunk_size:
                    if Config.up_zip == False:
                        multiFile.files.clear()
                    await C.edit(A.STR_COMPRIMIENDO.format(str(file)),buttons=None)
                    chunk_size = 1024 * 1024 * Config.ChunkSize
                    mult_file =  multiFile.MultiFile(file+'.7z',chunk_size)
                    zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
                    zip.write(file)
                    zip.close()
                    mult_file.close()
                    if Config.up_zip == True:
                        await C.edit('Partes de {} agregadas a la cola'.format(file_name),buttons=None)
                        return
                    for f in multiFile.files:
                        await C.edit(A.STR_SUBIENDO.format(str(f)),buttons=None)
                        Config.subiendo = 'Si'
                        Config.up_zip = True
                        if await B.login():
                            try:
                                U = await B.upload(f)
                                if U.get('event')=='fileexists':
                                    U=U.get('newfile')
                                U = U['url']
                                E = f + ':\n' + U.replace('\\','').replace('//','').replace(':','://') + '\n'
                                await D.send_message(H.chat_id, E)
                                os.unlink(f)
                            except Exception as u:				
                                await C.edit(A.STR_ERROR + str(u),buttons=None)
                                print(u)
                        else:
                            await C.edit(A.STR_ERROR,buttons=None)
                        Config.subiendo = 'No'
                        Config.up_zip = False
                        await C.edit('Proceso Finalizado!',buttons=None)
                else:
                    await C.edit(A.STR_SUBIENDO.format(str(file)),buttons=None)
                    Config.subiendo = 'Si'
                    if await B.login():
                            try:
                                u=await B.upload(file)
                                if u.get('event')=='fileexists':
                                    u=u.get('newfile')
                                u = u['url']
                                u = file+':\n'+u.replace('\\','').replace('//','').replace(':','://') + '\n'
                                await D.send_message(H.chat_id, u)
                            except Exception as k:				
                                await C.edit(A.STR_ERROR + str(k),buttons=None)
                    else:
                            await C.edit(A.STR_ERROR,buttons=None)
                    Config.subiendo = 'No'
                    await C.edit('Proceso Finalizado!',buttons=None)
                if B.upload_tasks==0:
                    await D.send_message(H.chat_id,A.STR_IDLE)


	@U(1)
	async def X(message,fname,received_bytes,total_bytes):
            total = total_bytes
            chunk = received_bytes
            await message.edit('📥Descargando {}\n\n▶️Progreso: {} %\n📊Descargado: {}\n📂Total: {}'.format(fname,round(chunk*100/total,2),sizeof_fmt(chunk),sizeof_fmt(total)),buttons=None)

	Y=R.get_event_loop()
	print('Listo.')
	#D.send_message(chat_id='1117027193', text='Bot Activo! :)')
	Y.run_forever()
