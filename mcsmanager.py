import requests

class MCSManagerAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Authorization': f'Bearer {self.api_key}'
        }

    def get_instance_list(self, daemon_id, page, page_size, instance_name=None, status=None):
        params = {
            'daemonId': daemon_id,
            'page': page,
            'page_size': page_size,
            'apikey': self.api_key
        }
        response = requests.get(f'{self.base_url}/api/service/remote_service_instances', headers=self.headers, params=params)
        return response.json()

    def get_instance_detail(self, uuid, daemon_id):
        params = {
            'uuid': uuid,
            'daemonId': daemon_id
        }
        response = requests.get(f'{self.base_url}/api/instance', headers=self.headers, params=params)
        return response.json()

    def create_instance(self, daemon_id, instance_config):
        params = {'daemonId': daemon_id}
        response = requests.post(f'{self.base_url}/api/instance', headers=self.headers, params=params, json=instance_config)
        return response.json()

    def update_instance_config(self, uuid, daemon_id, instance_config):
        params = {'uuid': uuid, 'daemonId': daemon_id}
        response = requests.put(f'{self.base_url}/api/instance', headers=self.headers, params=params, json=instance_config)
        return response.json()

    def delete_instance(self, daemon_id, uuids, delete_file=False):
        params = {'daemonId': daemon_id}
        data = {'uuids': uuids, 'deleteFile': delete_file}
        response = requests.delete(f'{self.base_url}/api/instance', headers=self.headers, params=params, json=data)
        return response.json()

    def start_instance(self, uuid, daemon_id):
        params = {'uuid': uuid, 'daemonId': daemon_id}
        response = requests.get(f'{self.base_url}/api/protected_instance/open', headers=self.headers, params=params)
        return response.json()

    def stop_instance(self, uuid, daemon_id):
        params = {'uuid': uuid, 'daemonId': daemon_id}
        response = requests.get(f'{self.base_url}/api/protected_instance/stop', headers=self.headers, params=params)
        return response.json()

    def restart_instance(self, uuid, daemon_id):
        params = {'uuid': uuid, 'daemonId': daemon_id}
        response = requests.get(f'{self.base_url}/api/protected_instance/restart', headers=self.headers, params=params)
        return response.json()

    def kill_instance(self, uuid, daemon_id):
        params = {'uuid': uuid, 'daemonId': daemon_id}
        response = requests.get(f'{self.base_url}/api/protected_instance/kill', headers=self.headers, params=params)
        return response.json()

    def batch_operation(self, operation, instances):
        if operation not in ['start', 'stop', 'restart', 'kill']:
            raise ValueError("Invalid operation. Must be one of: 'start', 'stop', 'restart', 'kill'.")
        url = f'{self.base_url}/api/instance/multi_{operation}'
        data = [{'instanceUuid': instance['uuid'], 'daemonId': instance['daemon_id']} for instance in instances]
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

    def update_instance(self, uuid, daemon_id):
        params = {'uuid': uuid, 'daemonId': daemon_id, 'task_name': 'update'}
        response = requests.get(f'{self.base_url}/api/protected_instance/asynchronous', headers=self.headers, params=params)
        return response.json()

    def send_command(self, uuid, daemon_id, command):
        params = {'uuid': uuid, 'daemonId': daemon_id, 'command': command}
        response = requests.get(f'{self.base_url}/api/protected_instance/command', headers=self.headers, params=params)
        return response.json()

    def get_output(self, uuid, daemon_id, size=None):
        params = {'uuid': uuid, 'daemonId': daemon_id, 'size': size}
        response = requests.get(f'{self.base_url}/api/protected_instance/outputlog', headers=self.headers, params=params)
        return response.json()

    def reinstall_instance(self, daemon_id, uuid, target_url, title, description):
        params = {'daemonId': daemon_id, 'uuid': uuid}
        data = {'targetUrl': target_url, 'title': title, 'description': description}
        response = requests.post(f'{self.base_url}/api/protected_instance/install_instance', headers=self.headers, params=params, json=data)
        return response.json()
