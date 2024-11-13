import requests


def find_leader(config):
    """
    Queries frontend for current leader
    :param config:
    :return:
    """
    try:
        leader_response = requests.get(f"{config['frontend_addr']}/{config['secret_key']}/whoisleader")
        if leader_response.status_code == 200:
            return leader_response.text
        else:
            return None
    except:
        return None


def sync_db_with_leader(config, replica_id, leader_url, db, sync_lock, transaction_handler):
    """
    Perform synchronization with the leader
    :param config:
    :param replica_id:
    :param leader_url:
    :param db:
    :param sync_lock:
    :param transaction_handler:
    :return:
    """
    with sync_lock:
        replica_url = config["replica_addr"].format(replica_id)
        if replica_url != leader_url:
            response = requests.get(f"{leader_url}/syncSendMulti/{db.get_max_key()}")
            if response.status_code == 200:
                data = response.json()
                if len(data) > 0:
                    db.write_multi(data)
                    transaction_handler.updateLastTransactionState(db)


def send_sync(config, transaction, leader_url):
    """
    Sends new order logs to the replicas
    :param config:
    :param transaction:
    :param leader_url:
    :return:
    """
    for replica_id in range(1, config["max_replicas"] + 1):
        replica_url = config["replica_addr"].format(replica_id)
        if replica_url != leader_url:
            try:
                replica_response = requests.post(f"{replica_url}/syncReceive", json=transaction, timeout=2)
            except:
                pass


def send_clear(config, leader_url):
    """
    Send clear DB requests to the replicas
    :param config:
    :param leader_url:
    :return:
    """
    for replica_id in range(1, config["max_replicas"] + 1):
        replica_url = config["replica_addr"].format(replica_id)
        if replica_url != leader_url:
            try:
                replica_response = requests.get(f"{replica_url}/clearDB/{config['secret_key']}", timeout=1)
            except:
                pass
