import json
import math
import re
import urllib.parse
from os import popen
from random import choice
from urllib.parse import urlparse
import lk21
import requests
from bs4 import BeautifulSoup
from js2py import EvalJs
from lk21.extractors.bypasser import Bypass
from base64 import standard_b64encode

def direct_link_generator(link: str):
    """ direct links generator """
    if 'zippyshare.com' in link:
        return zippy_share(link)
    elif 'yadi.sk' in link:
        return yandex_disk(link)
    elif 'cloud.mail.ru' in link:
        return cm_ru(link)
    elif "drive.google.com" in link:
        return gdrive(link)
    elif 'mediafire.com' in link:
        return mediafire(link)
    elif "mega." in link:
        return mega_dl(link)
    elif 'uptobox.com' in link:
        return uptobox(link)
    elif 'osdn.net' in link:
        return osdn(link)
    elif 'github.com' in link:
        return github(link)
    elif 'hxfile.co' in link:
        return racaty(link)
    elif 'anonfiles.com' in link:
        return anonfiles(link)
    elif 'letsupload.io' in link:
        return letsupload(link)
    elif 'fembed.net' in link:
        return fembed(link)
    elif 'fembed.com' in link:
        return fembed(link)
    elif 'femax20.com' in link:
        return fembed(link)
    elif 'fcdn.stream' in link:
        return fembed(link)
    elif 'feurl.com' in link:
        return fembed(link)
    elif 'naniplay.nanime.in' in link:
        return fembed(link)
    elif 'naniplay.nanime.biz' in link:
        return fembed(link)
    elif 'naniplay.com' in link:
        return fembed(link)
    elif 'layarkacaxxi.icu' in link:
        return fembed(link)
    elif 'sbembed.com' in link:
        return sbembed(link)
    elif 'streamsb.net' in link:
        return sbembed(link)
    elif 'sbplay.org' in link:
        return sbembed(link)
    elif '1drv.ms' in link:
        return onedrive(link)
    elif 'pixeldrain.com' in link:
        return pixeldrain(link)
    elif 'antfiles.com' in link:
        return antfiles(link)
    elif 'streamtape.com' in link:
        return streamtape(link)
    elif 'bayfiles.com' in link:
        return anonfiles(link)
    elif 'racaty.net' in link:
        return racaty(link)
    else:
        return False


def zippy_share(url: str) -> str:
    """ ZippyShare direct links generator
    Based on https://github.com/KenHV/Mirror-Bot
             https://github.com/jovanzers/WinTenCermin """
    try:
        link = re.findall(r'\bhttps?://.*zippyshare\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Zippyshare links found")
    try:
        base_url = re.search('http.+.zippyshare.com', link).group()
        response = requests.get(link).content
        pages = BeautifulSoup(response, "lxml")
        try:
            js_script = pages.find("div", {"class": "center"}).find_all("script")[1]
        except IndexError:
            js_script = pages.find("div", {"class": "right"}).find_all("script")[0]
        js_content = re.findall(r'\.href.=."/(.*?)";', str(js_script))
        js_content = 'var x = "/' + js_content[0] + '"'
        evaljs = EvalJs()
        setattr(evaljs, "x", None)
        evaljs.execute(js_content)
        js_content = getattr(evaljs, "x")
        return base_url + js_content
    except IndexError:
        raise DirectDownloadLinkException("Can't find download button")


def yandex_disk(url: str) -> str:
    """ Yandex.Disk direct links generator
    Based on https://github.com/wldhx/yadisk-direct """
    try:
        link = re.findall(r'\bhttps?://.*yadi\.sk\S+', url)[0]
    except IndexError:
        reply = "No Yandex.Disk links found\n"
        return reply
    api = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'
    try:
        dl_url = requests.get(api.format(link)).json()['href']
        return dl_url
    except KeyError:
        raise DirectDownloadLinkException("Error: File not found/Download limit reached\n")


def cm_ru(url: str) -> str:
    """ cloud.mail.ru direct links generator
    Using https://github.com/JrMasterModelBuilder/cmrudl.py """
    reply = ''
    try:
        link = re.findall(r'\bhttps?://.*cloud\.mail\.ru\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No cloud.mail.ru links found\n")
    command = f'vendor/cmrudl.py/cmrudl -s {link}'
    result = popen(command).read()
    result = result.splitlines()[-1]
    try:
        data = json.loads(result)
    except json.decoder.JSONDecodeError:
        raise DirectDownloadLinkException("Error: Can't extract the link\n")
    dl_url = data['download']
    return dl_url


def uptobox(url: str) -> str:
    """ Uptobox direct links generator
    based on https://github.com/jovanzers/WinTenCermin """
    try:
        link = re.findall(r'\bhttps?://.*uptobox\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Uptobox links found\n")
    if UPTOBOX_TOKEN is None:
        LOGGER.error('UPTOBOX_TOKEN not provided!')
        dl_url = link
    else:
        try:
            link = re.findall(r'\bhttp?://.*uptobox\.com/dl\S+', url)[0]
            dl_url = link
        except:
            file_id = re.findall(r'\bhttps?://.*uptobox\.com/(\w+)', url)[0]
            file_link = 'https://uptobox.com/api/link?token=%s&file_code=%s' % (UPTOBOX_TOKEN, file_id)
            req = requests.get(file_link)
            result = req.json()
            dl_url = result['data']['dlLink']
    return dl_url

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
        name = "Direct Download Link"
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
    reply += f"[{name}]({dl_url})\n"
    return reply

def mediafire(url: str) -> str:
    """ MediaFire direct links generator """
    try:
        link = re.findall(r'\bhttps?://.*mediafire\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No MediaFire links found\n")
    page = BeautifulSoup(requests.get(link).content, 'lxml')
    info = page.find('a', {'aria-label': 'Download file'})
    dl_url = info.get('href')
    return dl_url

def mega_dl(url: str) -> str:
    """MEGA.nz direct links generator
    Using https://github.com/tonikelope/megadown"""
    reply = ""
    try:
        link = re.findall(r"\bhttps?://.*mega.*\.nz\S+", url)[0]
    except IndexError:
        reply = "`No MEGA.nz links found`\n"
        return reply
    command = f"bin/megadown -q -m {link}"
    result = popen(command).read()
    try:
        data = json.loads(result)
        print(data)
    except json.JSONDecodeError:
        reply += "`Error: Can't extract the link`\n"
        return reply
    dl_url = data["url"]
    name = data["file_name"]
    size = naturalsize(int(data["file_size"]))
    reply += f"[{name} ({size})]({dl_url})\n"
    return reply


def osdn(url: str) -> str:
    """ OSDN direct links generator """
    osdn_link = 'https://osdn.net'
    try:
        link = re.findall(r'\bhttps?://.*osdn\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No OSDN links found\n")
    page = BeautifulSoup(
        requests.get(link, allow_redirects=True).content, 'lxml')
    info = page.find('a', {'class': 'mirror_link'})
    link = urllib.parse.unquote(osdn_link + info['href'])
    mirrors = page.find('form', {'id': 'mirror-select-form'}).findAll('tr')
    urls = []
    for data in mirrors[1:]:
        mirror = data.find('input')['value']
        urls.append(re.sub(r'm=(.*)&f', f'm={mirror}&f', link))
    return urls[0]


def github(url: str) -> str:
    """ GitHub direct links generator """
    try:
        re.findall(r'\bhttps?://.*github\.com.*releases\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No GitHub Releases links found\n")
    download = requests.get(url, stream=True, allow_redirects=False)
    try:
        dl_url = download.headers["location"]
        return dl_url
    except KeyError:
        raise DirectDownloadLinkException("Error: Can't extract the link\n")


def racaty(url: str) -> str:
    """ Racaty direct link generator
    Based on https://github.com/breakdowns/slam-mirrorbot """
    bypasser = lk21.Bypass()
    dl_url=bypasser.bypass_filesIm(url)
    return dl_url


def anonfiles(url: str) -> str:
    """ Anonfiles direct link generator
    Based on https://github.com/breakdowns/slam-mirrorbot """
    bypasser = lk21.Bypass()
    dl_url=bypasser.bypass_anonfiles(url)
    return dl_url


def letsupload(url: str) -> str:
    """ Letsupload direct link generator
    Based on https://github.com/breakdowns/slam-mirrorbot """
    dl_url = ''
    try:
        link = re.findall(r'\bhttps?://.*letsupload\.io\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Letsupload links found\n")
    bypasser = lk21.Bypass()
    dl_url=bypasser.bypass_url(link)
    return dl_url


def fembed(link: str) -> str:
    """ Fembed direct link generator
    Based on https://github.com/breakdowns/slam-mirrorbot """
    bypasser = lk21.Bypass()
    dl_url=bypasser.bypass_fembed(link)
    lst_link = []
    count = len(dl_url)
    for i in dl_url:
        lst_link.append(dl_url[i])
    return lst_link[count-1]


def sbembed(link: str) -> str:
    """ Sbembed direct link generator
    Based on https://github.com/breakdowns/slam-mirrorbot """
    bypasser = lk21.Bypass()
    dl_url=bypasser.bypass_sbembed(link)
    lst_link = []
    count = len(dl_url)
    for i in dl_url:
        lst_link.append(dl_url[i])
    return lst_link[count-1]


def onedrive(link: str) -> str:
    """ Onedrive direct link generator
    Based on https://github.com/UsergeTeam/Userge """
    link_without_query = urlparse(link)._replace(query=None).geturl()
    direct_link_encoded = str(standard_b64encode(bytes(link_without_query, "utf-8")), "utf-8")
    direct_link1 = f"https://api.onedrive.com/v1.0/shares/u!{direct_link_encoded}/root/content"
    resp = requests.head(direct_link1)
    if resp.status_code != 302:
        return "Error: Unauthorized link, the link may be private"
    dl_link = resp.next.url
    file_name = dl_link.rsplit("/", 1)[1]
    resp2 = requests.head(dl_link)
    return dl_link


def pixeldrain(url: str) -> str:
    """ Based on https://github.com/yash-dk/TorToolkit-Telegram """
    url = url.strip("/ ")
    file_id = url.split("/")[-1]
    info_link = f"https://pixeldrain.com/api/file/{file_id}/info"
    dl_link = f"https://pixeldrain.com/api/file/{file_id}"
    resp = requests.get(info_link).json()
    if resp["success"]:
        return dl_link
    else:
        raise DirectDownloadLinkException("ERROR: Cant't download due {}.".format(resp.text["value"]))


def antfiles(url: str) -> str:
    """ Antfiles direct link generator
    Based on https://github.com/breakdowns/slam-mirrorbot """
    bypasser = lk21.Bypass()
    dl_url=bypasser.bypass_antfiles(url)
    return dl_url


def streamtape(url: str) -> str:
    """ Streamtape direct link generator
    Based on https://github.com/breakdowns/slam-mirrorbot """
    bypasser = lk21.Bypass()
    dl_url=bypasser.bypass_streamtape(url)
    return dl_url


def useragent():
    """
    useragent random setter
    """
    useragents = BeautifulSoup(
        requests.get(
            'https://developers.whatismybrowser.com/'
            'useragents/explore/operating_system_name/android/').content,
        'lxml').findAll('td', {'class': 'useragent'})
    user_agent = choice(useragents)
    return user_agent.text