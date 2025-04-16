from .known_nodes import (
    add_or_update_peer,
    get_all_peers,
    remove_peer,
    create_table as create_peers_table
)

from .known_discovery_servers_table import (
    add_or_update_discovery,
    get_all_discovery_servers,
    remove_discovery_server,
    create_table as create_discovery_table
)
