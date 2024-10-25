import os
import sys
import zipfile
import datetime
import httpx as request
from loguru import logger
from tqdm.tk import tqdm

timeout=request.Timeout(10.0)
api_url="https://gitee.com/api/v5/repos/vc_teahouse/sjdm/releases/latest"


def check_update(localver:str):
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


def get_update():
    logger.info("checking...")
    try:
        respond=request.get(api_url,timeout=timeout)
    except:
        pass
    finally:
        if respond.status_code == 200:
            data=respond.json()['assets']
            for i in data:
                print(i)
                k=i["name"]
                j=i["browser_download_url"]
                if k =="随机点名.zip":
                    with request.stream(method="GET",url=j,follow_redirects=True,timeout=timeout) as r:
                        if r.status_code == 200:
                            size=int(r.headers.get('content-length',0))
                            bar=tqdm(total=size,unit='iB',unit_scale=True)
                            print(r)
                            with open("update.zip",'wb') as file:
                                    for chuck in r.iter_bytes(chunk_size=1024*200):
                                        file.write(chuck)
                                        bar.update(len(chuck))
                        else:
                            logger.info("failed!")
                    os.remove("随机点名.exe")
                    z=zipfile.ZipFile("update.zip",'r')
                    for i in z.namelist():
                        z.extract(i,os.getcwd())
                    os.remove("update.zip")
                    break

@logger.catch
def main():
    logger.info(sys.argv)
    logger.info(os.getcwd())
    args=sys.argv[1:]
    if args[0] == "update":
        get_update()
    else:
        check_update(args[0])





if __name__ == "__main__":
    today=datetime.date.today()
    logger.add(f"./res/logs/updater-{today}.log")
    main()