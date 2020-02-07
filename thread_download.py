from bs4 import BeautifulSoup as bs
from sys import argv
import os
import requests
from concurrent.futures import ThreadPoolExecutor as TPE
from time import sleep


def process_thread(link, pool, futures):
    # TODO: hash webms to see if already downloaded
    html = requests.get(link).text
    soup = bs(html, 'html.parser')

    # make folder titled after thread
    thread_dir = os.path.join(os.getcwd(), soup.find('span', {'class': 'subject'}).text.replace('/', ''))
    if not os.path.exists(thread_dir):
        os.makedirs(thread_dir)
        print(thread_dir + ' created!')
    else:
        print(f'{thread_dir} already exists')
        # TODO: pick up from where downlaoding left off in future
        quit(1)
    
    # download OP webm
    pool.submit(download, 'http:' + soup.find('div', {'class': 'postContainer opContainer'}).find('a')['href'], thread_dir)

    # go through all posts and download
    for post in soup.findAll('div', {'class': 'postContainer replyContainer'}):
        media = post.find('a', {'class': 'fileThumb'})
        if media != None:
            # start thread
            futures.append(pool.submit(download, 'http:' + media['href'], thread_dir))


def download(link, path):
    # writes webm to file
    r = requests.get(link, stream=True)
    if r.status_code == 200:
        with open(os.path.join(path, link.rsplit('/', 1)[1]), 'wb') as f:
            for chunk in r:
                f.write(chunk)
        print(f'{link} downloaded')
    else:
        print(f'Error downloading {link}')

if __name__ == '__main__':
    print('Downloading thread...')
    with TPE() as pool:
        futures = []
        process_thread(argv[1], pool, futures)
        while futures != []:
            for idx, f in enumerate(futures):
                if f.done():
                    if f.exception() != None:
                        print(f.exception())
                    futures.pop(idx)
            sleep(1)

    print('Done!')
