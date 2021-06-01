from bs4 import BeautifulSoup as bs
from sys import argv
import os
import requests
from concurrent.futures import ThreadPoolExecutor as TPE
from time import sleep


def process_thread(link, pool, futures):
    # TODO: hash webms to see if already downloaded
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    html = requests.get(link, headers={'User-Agent' : user_agent}).text
    soup = bs(html, 'html.parser')

    # make folder titled after thread
    thread_name = ''
    if len(argv) == 2:
        if '.moe' in link:
            thread_name = soup.find('h2', {'class': 'post_title'}).text.replace('/', '')
        else:
            thread_name = soup.find('span', {'class': 'subject'}).text.replace('/', '')
    else:
        thread_name = argv[2]
    thread_dir = os.path.join(os.getcwd(), thread_name)
    if not os.path.exists(thread_dir):
        os.makedirs(thread_dir)
        print(thread_dir + ' created!')
    else:
        while True:
            choice = input(f'{thread_dir} already exists, check for new media? (y/n)\n')
            if choice == 'y':
                break
            elif choice == 'n':
                quit(1)
    
    if '.moe' not in link:
        # download OP webm
        pool.submit(download, 'http:' + soup.find('div', {'class': 'postContainer opContainer'}).find('a')['href'], thread_dir)

        # go through all posts and download
        for post in soup.findAll('div', {'class': 'postContainer replyContainer'}):
            media = post.find('a', {'class': 'fileThumb'})
            if media != None:
                # start thread
                fname = post.find('div', {'class': 'fileText'}).find('a').text
                futures.append(pool.submit(download, 'http:' + media['href'], thread_dir, fname))
    else:  # this sux but works
        for idx, post in enumerate(soup.findAll('a', {'class': 'thread_image_link'})):
            futures.append(pool.submit(download, post['href'], thread_dir, str(idx) + '.' +post['href'].rsplit('.', 1)[1]))


def download(link, path, name):
    # check if file exists
    filename = os.path.join(path, name)
    if os.path.isfile(filename):
        print(f'{name} already exists!')
    else:
        # writes webm to file
        r = requests.get(link, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
            print(f'{name} downloaded')
        else:
            print(f'Error downloading {link}, code: {r.status_code}')

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
            sleep(0.25)

    print('Done!')
