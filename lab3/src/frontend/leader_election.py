import threading

import requests
def perform_election(frontend_config):
    """
    Performs leader election by sending requests to replicas
    :param frontend_config:
    :return:
    """
    leader_url = None
    candidates = []

    for candidate in range(1, frontend_config["max_replicas"] + 1):
        try:
            replica_url = frontend_config["replica_addr"].format(candidate)
            response = requests.get(f"{replica_url}/ping")
            if response.status_code == 200:
                candidate_id = int(response.text)
                candidates.append(candidate_id)
        except:
            pass

    if len(candidates) > 0:
        leader_id = max(candidates)
        leader_url = frontend_config["replica_addr"].format(leader_id)
        for candidate in candidates:
            try:
                replica_url = frontend_config["replica_addr"].format(candidate)
                response = requests.get(f"{replica_url}/announceLeader/{leader_id}")
            except:
                pass

    return leader_url