import requests

def getrequest(location:str,params:dict = {}):
    # Define the API URL and parameters
    url = "http://verweij.site:23333" + location
    api_key = "1a09d7a8a0b141aba376be08cccc38f2"

    # Set up headers
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest"
    }

    # Add the API key as a query parameter
    params["apikey"] = api_key
    try:
        # Send GET request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        # Print response
        #print("Response Status Code:", response.status_code)
        #print("Response Body:", response.json())
        result = response.json()
        return result
    except requests.exceptions.RequestException as e:
        print("Error during the request:", e)
result = getrequest("/api/protected_instance/open",{
    "uuid":"f00b41a39ff849a19335b34686bdce94",
    "daemonId":"301318d9a9c340a583082c72d73690f3"
})
pass