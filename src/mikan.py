# -*- coding: utf-8 -*-
import sys
import json
from workflow import Workflow3, ICON_SYNC, ICON_EJECT, ICON_WARNING
from workflow.background import run_in_background


def show_RSS_items(posts):
    settings = json.loads(open('mikan_settings.json', 'r').read())
    filters = settings.get('filters', {})
    history = wf.stored_data('downloaded') or set()
    for info in posts:
        if not all(x in info['title'] for x in filters.get(info['name'], [])):
            continue

        item = wf.add_item(
            title=info['title'],
            subtitle='publish date: {0}, size: {1}'.format(info['pubdate'], info['size']),
            largetext=info['title'],
            icon=ICON_EJECT if info['key'] not in history else ICON_SYNC,
            quicklookurl=info['cover']
        )
        item.add_modifier(
            key='cmd',
            subtitle='Download by magnet link',
            arg=info['title'] + u'#' + info['key'] + u'#' + info['name'] + u'#' + info['magnet'],
            valid=True
        )
        item.add_modifier(
            key='alt',
            subtitle='Download by torrent',
            arg=info['title'] + u'#' + info['key'] + u'#' + info['name'] + u'#' + info['torrent'],
            valid=True
        )
        item.add_modifier(
            key='fn',
            subtitle='Copy meta-data to clipboard',
            arg=u'\n'.join([u'{}: {}'.format(k, v) for k, v in info.iteritems()]),
            valid=True
        )
        item.add_modifier(
            key='ctrl',
            subtitle='Go to series home page',
            arg=info['series_page'],
            valid=True
        )
        item.add_modifier(
            key='shift',
            subtitle=info['title'],
            valid=False
        )


def main(wf):
    query = wf.args[0]
    # Get posts from cache. Set `data_func` to None, as we don't want to
    # update the cache in this script and `max_age` to 0 because we want
    # the cached data regardless of age
    posts = wf.cached_data('posts', None, max_age=0)

    # Start update script if cached data are too old (or doesn't exist)
    if not wf.cached_data_fresh('posts', max_age=1200):
        cmd = ['/usr/bin/python', wf.workflowfile('update.py')]
        run_in_background('update', cmd)

    # If script was passed a query, use it to filter posts if we have some
    if query and posts:
        posts = wf.filter(query, posts, key=lambda x: x['title'])

    # If we have no data to show, so show a warning and stop
    if not posts:
        wf.add_item('No posts found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    show_RSS_items(posts)
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
