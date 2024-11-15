import os
import sys
import zipfile
import datetime
import httpx as request
from time import sleep
from loguru import logger
from tqdm.tk import tqdm
from dotenv import load_dotenv

timeout=request.Timeout(10.0)
cancel_update=False

def add_token():
    global api_url
    api_url=str("https://gitee.com/api/v5/repos/vc_teahouse/sjdm/releases/latest")
    failed=False
    token=""
    load_dotenv(dotenv_path=".env")
    try:
        token=os.environ["access_token"]
    except KeyError:
        failed=True
        return
    finally:
        if failed:
            logger.info("No access_token found in .env file!")
        else:
            api_url=api_url+f"?access_token={token}"
        logger.info(f"Using access_token:{token}")

def check_update(localver:str="v1.2.0-200424"): # 检测更新，已弃用
    logger.info("checking...")
    try:
        respond=request.get(api_url,timeout=timeout)
    except:
        logger.info("failed!")
        raise
    finally:
        print(respond)
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
                            bar=tqdm(total=size,unit='iB',unit_scale=True,desc="正在下载更新，请不要关闭窗口...",cancel_callback=close_window)
                            print(r)
                            with open("update.zip",'wb') as file:
                                    for chuck in r.iter_bytes(chunk_size=1024*300):
                                        if cancel_update:
                                            file.close()
                                            os.remove("update.zip")
                                            bar.close()
                                            logger.info("Update cancelled by user,now starting...")
                                            start()
                                            os._exit(0)
                                        else:
                                            file.write(chuck)
                                            bar.update(len(chuck))
                                            bar.refresh()
                                    file.close()
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
        else:
            logger.exception(f"{respond.text}")

def start(): # after update
    os.system("cmd /c start 随机点名.exe")

def close_window(): # cancel update
    global cancel_update
    cancel_update=True
    return

@logger.catch
def main():
    logger.info(sys.argv)
    logger.info(os.getcwd())
    if len(sys.argv) == 1: # no args
        logger.info("No args,exiting...")
        os._exit(0)
    args=sys.argv[1:]
    add_token()
    logger.info("Inirtialized,starting...")
    if args[0] == "update":
        get_update()
    else:
        check_update()

if __name__ == "__main__":
    today=datetime.date.today()
    logger.add(f"./updatelogs/updater-{today}.log")
    main()