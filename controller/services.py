import logging
import requests
from json.decoder import JSONDecodeError

from smart_home.settings import SMART_HOME_ACCESS_TOKEN, SMART_HOME_API_URL

logger = logging.getLogger(__name__)


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
    try:
        data = {
            'controllers': [{'name': name, 'value': value}
                            for name, value in states.items()]
        }
        logger.debug(f'Save: {data}')
        r = requests.post(
            SMART_HOME_API_URL,
            json=data,
            headers={'Authorization': f'Bearer {SMART_HOME_ACCESS_TOKEN}'},
            timeout=10
        )
    except requests.RequestException as e:
        raise SmartHomeControllerError(repr(e))
