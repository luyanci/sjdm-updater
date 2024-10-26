import os
import sys
import zipfile
import datetime
from time import sleep
import httpx as request
from loguru import logger
from tqdm.tk import tqdm

timeout=request.Timeout(10.0)
api_url="https://gitee.com/api/v5/repos/vc_teahouse/sjdm/releases/latest"


def check_update(localver:str="v1.2.0-200424"): # 检测更新，已弃用
    logger.info("checking...")
    try:
        respond=request.get(api_url,timeout=timeout)
    except:
        pass
    finally:
        if respond.status_code == 200:
            data=respond.json()
            logger.info(f"Upstream:{data['tag_name']}")
            if data["tag_name"] != localver:
                logger.info("Found Update!")
                return True
            else:
                return False


def get_update(): # 获取更新
    logger.info("checking...")
    try:
        respond=request.get(api_url,timeout=timeout)
    except:
        pass
    finally:
        if respond.status_code == 200:
            data=respond.json()['assets']
            for i in data:
                logger.info(i)
                k=i["name"]
                j=i["browser_download_url"]
                if k =="随机点名.zip":
                    with request.stream(method="GET",url=j,follow_redirects=True,timeout=timeout) as r:
                        if r.status_code == 200:
                            logger.info("downloading...")
                            size=int(r.headers.get('content-length',0))
                            bar=tqdm(total=size,unit='iB',unit_scale=True)
                            print(r)
                            with open("update.zip",'wb') as file:
                                    for chuck in r.iter_bytes(chunk_size=1024*500):
                                        file.write(chuck)
                                        bar.update(len(chuck))
                        else:
                            logger.info("failed!")
                    try:
                        os.remove("随机点名.exe")
                    except FileNotFoundError:
                        pass
                    z=zipfile.ZipFile("update.zip",'r')
                    for i in z.namelist():
                        z.extract(i,os.getcwd())
                        os.rename(i,"随机点名.exe")
                        z.close()
                    os.remove("update.zip")
                    logger.info("update successfully!Starting...")
                    sleep(1)
                    start()
                    os._exit(0)

def start(): # after update
    os.system("cmd /c start 随机点名.exe")
@logger.catch
def main():
    logger.info(sys.argv)
    logger.info(os.getcwd())
    args=sys.argv[1:]
    logger.info("Inirtialized,starting...")
    if args[0] == "update":
        get_update()
    else:
        check_update()





if __name__ == "__main__":
    today=datetime.date.today()
    logger.add(f"./updatelogs/updater-{today}.log")
    main()