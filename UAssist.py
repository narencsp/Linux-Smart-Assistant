
from __future__ import print_function

import json
import yaml
import os.path
import argparse
import subprocess
import pathlib2 as pathlib

import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file
from google.assistant.library.device_helpers import register_device

from actions import Actions
from actions import openFun
from actions import closeFun
from actions import openFileOption

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

WARNING_NOT_REGISTERED = """
    This device is not registered. This means you will not be able to use
    Device Actions or see your device in Assistant Settings. In order to
    register this device follow instructions at:

    https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device
"""


class Myassistant:
    thread = 0
    with open('{}/resource/yaml/keywords.yaml'.format(Actions.ROOT_PATH), 'r') as conf:
        custom_action_keyword = yaml.load(conf)

    def customAction(self, comand):
        if not comand:
            return
        dic = {0: 'first', 1: 'second', 2: 'third', 3: 'fourth', 4: 'fifth', 5: 'quit'}
        opt = [key for key, value in dic.items() if value in str(comand).lower()]
        if Actions.ON_CUSTOM_RESPONDING_OPEN and opt:
            self.uassistant.stop_conversation()
            print('ON_CUSTOM_ACTION_TURN_CONTINUED')
            openFileOption(fileLoc=Actions.ON_CUSTOM_RESPONDING_OPEN, tst=opt[0])
            print('ON_CUSTOM_ACTION_TURN_FINISHED')

        elif (self.custom_action_keyword['keywords']['open'][0]).lower() in str(comand).lower():
            self.uassistant.stop_conversation()
            print('ON_CUSTOM_ACTION_TURN_STARTED')
            openFun(str(comand).lower(), uassistant=self.uassistant)
            print('ON_CUSTOM_ACTION_TURN_FINISHED')
        elif (self.custom_action_keyword['keywords']['close'][0]).lower() in str(comand).lower():
            self.uassistant.stop_conversation()
            print('ON_CUSTOM_ACTION_TURN_STARTED')
            closeFun(str(comand).lower())
            print('ON_CUSTOM_ACTION_TURN_FINISHED')

    def processEvent(self, event):
        """Pretty prints events.
        Prints all events that occur with two spaces between each new
        conversation and a single space between turns of a conversation.
        Args:
            event(event.Event): The current event to process.
        """
        print(event)
        Actions.status_text.set(str(event.type)[10:])

        # chat update
        if event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
            Actions.inp = event.args["text"]
            Actions.otp = ""
            Actions.text_text.set(Actions.inp)
            self.customAction(event.args)


        if event.type == EventType.ON_RENDER_RESPONSE:
            Actions.otp = event.args["text"]

        if event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
            Actions.text_text.set("")
            # Actions.chatUpdate('', 0)
            Actions.chatUpdate(Actions.inp, 1)  # You:
            Actions.chatUpdate(Actions.otp, 2)  # UAssist:

        if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            self.can_start_conversation = False
            subprocess.Popen(["aplay", "{}/resource/audio/todon.wav".format(Actions.ROOT_PATH)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if event.type == EventType.ON_DEVICE_ACTION:
            for command, params in event.actions:
                print('Do command', command, 'with params', str(params))

    def main(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--device-model-id', '--device_model_id', type=str,
                            metavar='DEVICE_MODEL_ID', required=False,
                            help='the device model ID registered with Google')
        parser.add_argument('--project-id', '--project_id', type=str,
                            metavar='PROJECT_ID', required=False,
                            help='the project ID used to register this device')
        parser.add_argument('--device-config', type=str,
                            metavar='DEVICE_CONFIG_FILE',
                            default=os.path.join(
                                os.path.expanduser('~/.config'),
                                'googlesamples-assistant',
                                'device_config_library.json'
                            ),
                            help='path to store and read device configuration')
        parser.add_argument('--credentials', type=existing_file,
                            metavar='OAUTH2_CREDENTIALS_FILE',
                            default=os.path.join(
                                os.path.expanduser('~/.config'),
                                'google-oauthlib-tool',
                                'credentials.json'
                            ),
                            help='path to store and read OAuth2 credentials')
        parser.add_argument('-v', '--version', action='version',
                            version='%(prog)s ' + Assistant.__version_str__())

        args = parser.parse_args()
        with open(args.credentials, 'r') as f:
            credentials = google.oauth2.credentials.Credentials(token=None,
                                                                **json.load(f))

        device_model_id = None
        last_device_id = None
        try:
            with open(args.device_config) as f:
                device_config = json.load(f)
                device_model_id = device_config['model_id']
                last_device_id = device_config.get('last_device_id', None)
        except FileNotFoundError:
            pass

        if not args.device_model_id and not device_model_id:
            raise Exception('Missing --device-model-id option')

        # Re-register if "device_model_id" is given by the user and it differs
        # from what we previously registered with.
        should_register = (
            args.device_model_id and args.device_model_id != device_model_id)

        device_model_id = args.device_model_id or device_model_id
        with Assistant(credentials, device_model_id) as assistant:
            self.uassistant = assistant
            events = assistant.start()
            device_id = assistant.device_id
            print('device_model_id:', device_model_id)
            print('device_id:', device_id + '\n')

            # Re-register if "device_id" is different from the last "device_id":
            if should_register or (device_id != last_device_id):
                if args.project_id:
                    register_device(args.project_id, credentials,
                                    device_model_id, device_id)
                    pathlib.Path(os.path.dirname(args.device_config)).mkdir(
                        exist_ok=True)
                    with open(args.device_config, 'w') as f:
                        json.dump({
                            'last_device_id': device_id,
                            'model_id': device_model_id,
                        }, f)
                else:
                    print(WARNING_NOT_REGISTERED)

            for event in events:
                if Myassistant.thread == 2:
                    Myassistant.thread = 0
                    Actions.btn_text.set('Start')
                    Actions.status_text.set('Not Listening')
                    break
                elif Myassistant.thread == 0:
                    Actions.btn_text.set('Start')
                    Actions.status_text.set('Not Listening')
                    break
                self.processEvent(event)


if __name__ == '__main__':
    try:
        Myassistant().main()
    except Exception as error:
        raise error
