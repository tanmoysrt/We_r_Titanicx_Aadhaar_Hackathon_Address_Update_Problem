import requests

def get_client_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    except:
        return None


def getLocationDetails(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        if res["status"] == "success":
            payload = {
                'ip': ip,
                'location_details': {
                    'lat': res["lat"],
                    'lon': res['lon'],
                    'city': res["city"],
                    'region': res["region"],
                    'country': res["country"],
                    'zip': res['zip']
                },
                'provider': {
                    'isp': res['isp'],
                    'org': res['org'],
                    'as': res['as']
                }

            }
            return True, payload
        else:
            return False, {}

    except:
        return False, {}

# print(getLocationDetails("47.11.103.137"))