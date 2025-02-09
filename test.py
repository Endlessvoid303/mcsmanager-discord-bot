import mcsmanager
base_url = 'http://verweij.site:23333'  # Replace with your MCSManager server URL
api_key = '1a09d7a8a0b141aba376be08cccc38f2'  # Replace with your API key

mcs_api = mcsmanager.MCSManagerAPI(base_url, api_key)

# Example: Get instance list
daemon_id = '301318d9a9c340a583082c72d73690f3'  # Replace with your daemon ID
page = 1
page_size = 10
instance_list = mcs_api.get_instance_list(daemon_id, page, page_size)
print(instance_list)