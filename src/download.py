# encoding: utf-8
import os
import json
import xmlrpclib
from workflow import Workflow3
from workflow.notify import notify


def main(wf):
    try:
        title, key, name, uri = wf.args[0].split(u'#')
        title, name = title.replace('\ ', ' '), name.replace('\ ', ' ')
        # Read settings
        settings = json.loads(open('mikan_settings.json', 'r').read())
        # Add new task to aria2c
        rpc_path = settings.get('rpc_path', 'http://localhost:6800/rpc')
        secret = 'token:' + settings.get('secret', '')
        server = xmlrpclib.ServerProxy(rpc_path).aria2
        dir_root = settings.get('download_root', '')
        if dir_root == '':
            server.addUri(secret, [uri])
        else:
            folder = os.path.join(dir_root, name)
            if not os.path.exists(folder):
                os.system(u'mkdir "{}"'.format(folder).encode('utf-8').strip())
            server.addUri(secret, [uri], {'dir': folder})
        # Update download history
        history = wf.stored_data('downloaded') or set()
        wf.store_data('downloaded', history | {key})
        # Write log and push notification
        wf.logger.debug('Downloading from link'.format(uri))
        notify('Download proceed', title)
    except Exception as err:
        wf.logger.error('Failed to add task')
        notify('Download failed', title)


if __name__ == '__main__':
    wf = Workflow3()
    wf.run(main)
