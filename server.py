from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs
import re
import os
folder = 'assets'
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            info = """
            Available endpoints:

            - GET /: Displays instructions about endpoints.

            - GET /image/<filename>: Returns the requested image from the 'assets' folder if it exists, error if doesn't.

            - POST /filedata: Accepts a path to the text file and a string to search for in json, and returns lenght of text file,
              amount of alphanumerical symbols in it and amout of occurences of searched string in the text file.
              Example of json:
              {
                "file_path": "path_to_file/test.txt",
                "search_string": "test"
              }
            
            - POST /urlinfo: Accepts a URL in json, parses it, and provides human-readable information about it.
            Example of json:
              {
                "url": "https://testurl.com/mypath/deeper?param1=xxx&param2=qqq"
              }
            """
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(info.encode('utf-8'))
        elif self.path.startswith('/image/'):
            filename = self.path[7:]
            image_path = os.path.join(os.path.dirname(__file__), folder, filename)
            if os.path.isfile(image_path):
                with open(image_path, 'rb') as file:
                    image_data = file.read()
                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg') 
                self.end_headers()
                self.wfile.write(image_data)
            else:
                self.send_error(404, f"Image {filename} not found in server folder")
        else:
            self.send_error(404, "No such request found")

    def do_POST(self):
        if self.path == '/filedata':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            file_path = data.get('file_path')
            search_string = data.get('search_string')
            with open(file_path, 'r') as file:
                file_content = file.read()
            response_data = {
                'length': len(file_content),
                'alphanumeric_symbols': sum(c.isalnum() for c in file_content),
                'occurrences': len(re.findall(search_string, file_content, re.IGNORECASE))
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        elif self.path == '/urlinfo':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            url = data.get('url')
            parsed_url = urlparse(url)
            path_steps = len(parsed_url.path.strip('/').split('/'))
            query_parameters = parse_qs(parsed_url.query)
            response_data = f"Url has {parsed_url.scheme} protocol;\n"
            response_data += f"Domain is '{parsed_url.netloc}';\n"
            response_data += f"The path to the resource has {path_steps} steps: {', '.join(parsed_url.path.strip('/').split('/'))};\n"
            response_data += "Query parameters: " + ', '.join([f"{key}: {value[0]}" for key, value in query_parameters.items()]) + "."
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(response_data.encode('utf-8'))
        else:
            self.send_error(404, "No such request found")

def run(server_class=HTTPServer, handler_class=RequestHandler, port=4000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Server listens to port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
