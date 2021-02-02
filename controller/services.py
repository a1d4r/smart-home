import requests
from json.decoder import JSONDecodeError

from smart_home.settings import SMART_HOME_ACCESS_TOKEN, SMART_HOME_API_URL


class SmartHomeControllerError(Exception):
    pass


def get_controllers_states():
    try:
        r = requests.get(
            SMART_HOME_API_URL,
            headers={'Authorization': f'Bearer {SMART_HOME_ACCESS_TOKEN}'},
            timeout=10
        )
        data = r.json()['data']
        states = {state['name']: state['value'] for state in data}
    except requests.RequestException as e:
        raise SmartHomeControllerError(repr(e))
    except JSONDecodeError as e:
        raise SmartHomeControllerError(repr(e))
    except KeyError as e:
        raise SmartHomeControllerError(repr(e))
    else:
        return states


def save_controller_state(states):
    print('Save:', states)
