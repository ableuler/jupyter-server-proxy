from .handlers import setup_handlers
from .config import ServerProxy as ServerProxyConfig, make_handlers, get_entrypoint_server_processes, make_server_process
from jupyter_server.utils import url_path_join as ujoin
from .api import ServersInfoHandler, IconHandler

# Jupyter Extension points
def _jupyter_server_extension_points():
    return [{
        'module': 'jupyter_server_proxy',
    }]

def _jupyter_nbextension_paths():
    return [{
        "section": "tree",
        "dest": "jupyter_server_proxy",
        'src': 'static',
        "require": "jupyter_server_proxy/tree"
    }]


def _load_jupyter_server_extension(nbapp):
    # Set up handlers picked up via config
    base_url = nbapp.web_app.settings['base_url']
    serverproxy_config = ServerProxyConfig(parent=nbapp)

    server_processes = [
        make_server_process(name, server_process_config, serverproxy_config)
        for name, server_process_config in serverproxy_config.servers.items()
    ]
    server_processes += get_entrypoint_server_processes(serverproxy_config)
    server_handlers = make_handlers(base_url, server_processes)
    nbapp.web_app.add_handlers('.*', server_handlers)

    # Set up default non-server handler
    setup_handlers(
        nbapp.web_app,
        serverproxy_config,
    )

    icons = {}
    for sp in server_processes:
        if sp.launcher_entry.enabled and sp.launcher_entry.icon_path:
            icons[sp.name] = sp.launcher_entry.icon_path

    nbapp.web_app.add_handlers('.*', [
        (ujoin(base_url, 'server-proxy/servers-info'), ServersInfoHandler, {'server_processes': server_processes}),
        (ujoin(base_url, 'server-proxy/icon/(.*)'), IconHandler, {'icons': icons}),
    ])


# For backward compatibility
load_jupyter_server_extension = _load_jupyter_server_extension
