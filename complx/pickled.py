import webview as wv
import urllib.request
import urllib.error

SHOWN = 'SHOWN'
LOADED = 'LOADED'

def is_reachable(url, q):
    try:
        response = urllib.request.urlopen(url)
        res = response.status < 400
    except (ValueError, urllib.error.URLError, urllib.error.HTTPError):
        res = False
    q.put(res)

def _onshown(q):
    q.put(SHOWN)
    
def _onload(q):
    q.put(LOADED)

def search(url, q):
    win = wv.create_window(
        '',
        url
    )
    win.events.loaded += lambda: _onload(q)
    win.events.shown += lambda: _onshown(q)
    wv.start()
    
if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()