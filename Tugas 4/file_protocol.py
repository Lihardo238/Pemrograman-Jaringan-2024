import json
import logging
import shlex
import base64
from file_interface import FileInterface

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()

    def process_string(self, incoming_string=''):
        logging.warning(f"Processing string: {incoming_string}")
        command_parts = shlex.split(incoming_string)
        try:
            command = command_parts[0].strip().lower()
            logging.warning(f"Processing command: {command}")
            if command == "upload":
                filename = command_parts[1]
                file_data = command_parts[2]
                decoded_data = base64.b64decode(file_data)
                with open(filename, 'wb') as f:
                    f.write(decoded_data)
                return json.dumps({"status": "OK", "data": "File uploaded successfully"})
            else:
                params = [param for param in command_parts[1:]]
                command_method = getattr(self.file, command)
                result = command_method(params)
                return json.dumps(result)
        except AttributeError as e:
            logging.warning(f"Unknown command: {command} - {e}")
            return json.dumps(dict(status='ERROR', data='Unknown request'))
        except Exception as e:
            logging.warning(f"Error processing command: {e}")
            return json.dumps(dict(status='ERROR', data=str(e)))

if __name__ == '__main__':
    # Example usage
    fp = FileProtocol()
    print(fp.process_string("LIST"))
    print(fp.process_string("GET example.jpg"))
    print(fp.process_string('UPLOAD example.jpg somebase64string'))
