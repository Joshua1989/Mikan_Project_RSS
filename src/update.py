# encoding: utf-8
import json
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
from workflow import Workflow3, web


def parse(item):
    key = item.enclosure['url'].split('/')[-1].split('.')[0]
    page = web.get('https://mikanani.me/Home/Episode/' + key)
    temp = BeautifulSoup(page.content, 'html.parser')
    info = {
        'key': key,
        'series_page': 'https://mikanani.me' + temp.find_all('div', attrs={'class': 'bangumi-poster'})[0]['onclick'][13:-13].split('#')[0],
        'cover': 'https://mikanani.me' + temp.find_all('div', attrs={'class': 'bangumi-poster'})[0]['style'][23:-3],
        'name': temp.find_all('p', attrs={'class': 'bangumi-title'})[0].a.string.replace(':', '-'),
        'title': item.guid.string,
        'size': item.description.string[len(item.guid.string) + 1:-1],
        'pubdate': item.pubdate.string.replace('T', ' '),
        'link': 'https://mikanani.me/Home/Episode/' + key,
        'torrent': item.enclosure['url'],
        'magnet': temp.find_all('a', attrs={'class': 'btn episode-btn'})[1]['href']
    }
    return info


def update_RSS(token):
    r = web.get('https://mikanani.me/RSS/MyBangumi?token=' + token)
    soup = BeautifulSoup(r.content, 'html.parser')
    p = ThreadPool()
    posts = p.map(parse, soup.find_all('item'))
    p.close()
    return posts


def main(wf):
    settings = json.loads(open('mikan_settings.json', 'r').read())
    token = settings.get('mikan_token', '')
    if token:
        # Get posts from RSS
        posts = wf.cached_data('posts', lambda: update_RSS(token), max_age=1 if wf.args[0] == 'force' else 1200)
        # Update download history
        history = wf.stored_data('downloaded') or set()
        wf.store_data('downloaded', history & {post['key'] for post in posts})
        # Write log
        wf.logger.debug('{} Mikan posts cached'.format(len(posts)))
    else:
        wf.logger.error('No Mikan token saved')


if __name__ == '__main__':
    wf = Workflow3()
    wf.run(main)
