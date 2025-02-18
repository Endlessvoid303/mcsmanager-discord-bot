import requests
import os
def request(location:str, params:dict,method:str="get",body = None):
    # Define the API URL and parameters
    response = None
    url = "http://verweij.site:23333" + location
    api_key = os.getenv("MCSMANAGER_APIKEY")
    # Set up headers
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest"
    }

    # Add the API key as a query parameter
    params["apikey"] = api_key
    try:
        # Send GET request
        if method == "get":
            response = requests.get(url, headers=headers, params=params,json=body)
        elif method == "post":
            response = requests.post(url, headers=headers, params=params,json=body)
        elif method == "delete":
            response = requests.delete(url, headers=headers, params=params,json=body)
        elif method == "put":
            response = requests.put(url, headers=headers, params=params,json=body)
        else:
            raise "method not valid"
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        # Print response
        #print("Response Status Code:", response.status_code)
        #print("Response Body:", response.json())
    except requests.exceptions.RequestException as e:
        print("Error during the request:", e)
        print(F"result: {response.json()}")
    else:
        result = response.json()
        return result
    return response.json()

def get_daemon_data():
    data = request("/api/overview", {})
    return data

def get_users(page: int, pagesize: int, user_name: str = "", role: str = ""):
    data = request("/api/auth/search", {"userName":user_name, "page":page, "page_size":pagesize, "role":role})
    return data

def start_instance(uuid:str):
    return request("/api/protected_instance/open", {"uuid":uuid, "daemonId": "301318d9a9c340a583082c72d73690f3"})

def stop_instance(uuid:str):
    return request("/api/protected_instance/stop", {"uuid":uuid, "daemonId": "301318d9a9c340a583082c72d73690f3"})

def restart_instance(uuid:str):
    return request("/api/protected_instance/restart", {"uuid":uuid, "daemonId": "301318d9a9c340a583082c72d73690f3"})

def add_user(username:str,password:str,permission:int):
    return request("/api/auth",{},"post",{"username": username,"password": password,"permission": permission})

def delete_user(uuid:str):
    return request("/api/auth",{},"delete",[uuid])

def create_server(daemon:str,name:str,ports:list,servertype:str,memory:int,version:str="latest"):
    env_vars = [
  "EULA=TRUE",
  F"MAX_MEMORY={memory}g",
  "ENABLE_AUTOSTOP=TRUE",
  "AUTOSTOP_TIMEOUT_EST=300",
  "AUTOSTOP_TIMEOUT_INIT=600",
  F"TYPE={servertype}",
  F"VERSION={version}"
]
    data = {
  "nickname": name,
  "startCommand": "",
  "stopCommand": "stop",
  "cwd": ".",
  "ie": "utf-8",
  "oe": "utf-8",
  "processType": "docker",
  "type": "minecraft/java",
  "tag": [],
  "endTime": "",
  "docker": {
    "containerName": "",
    "image": "itzg/minecraft-server",
    "ports": ports,
    "extraVolumes": [],
    "networkMode": "bridge",
    "networkAliases": [],
    "cpusetCpus": "",
    "maxSpace": 0,
    "workingDir": "/data/",
    "env": env_vars
  }
}
    return request("/api/instance",{"daemonId":daemon},"post",data)