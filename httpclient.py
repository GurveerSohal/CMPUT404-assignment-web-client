#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Copyright 2023 Gurveer Singh Sohal
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
import json

responseForUser = ""

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        status = data.strip("\r\n").split("\r\n")[0]
        code = int(status.split()[1])
        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        data = data.strip("\r\n").strip().split("\r\n")
        i = 0
        while i < len(data):
            if data[i] == '':
                i += 1
                break
            i += 1
        body = ""
        while i < len(data):
            body += data[i]
            i += 1
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        res = ""
        
        res =  buffer.decode('utf-8')

        return res

    def GET(self, url, args=None):
        global responseForUser
        request = []

        parsedURL = urllib.parse.urlparse(url)

        if parsedURL.scheme != "http":
            print("Include http:// in the url!")
            sys.exit(1)
        path = parsedURL.path
        if path == '':
            path = '/'

        if ' ' in path:
            path = ''.join(path.strip().split())

        queryString = "?"
        if parsedURL.query != "":
            queryString += parsedURL.query

        if args is not None:
            l = []
            for k in args:
                l.append(f"{k}={args[k]}")
            if len(queryString) == 1:
                queryString += '&'.join(l)
            else:
                queryString += '&' + '&'.join(l)

        if len(queryString) > 1:
            path += queryString

        request.append(f"GET {path} HTTP/1.1")

        request.append(f"Host: {parsedURL.hostname}")

        request.append("Accept: */*; charset=utf-8")

        request.append("Connection: close")

        data = "\r\n".join(request)
        data += "\r\n\r\n"

        host = parsedURL.hostname
        port = 80
        try:
            port = parsedURL.port
            if port is None:
                port = 80
        except ValueError:
            port = 80

        print(data)

        self.connect(host, port)
        self.sendall(data)
        response = self.recvall(self.socket)
        self.close()

        responseForUser = response

        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        global responseForUser
        request = []

        parsedURL = urllib.parse.urlparse(url)

        path = parsedURL.path

        if path == '':
            path = '/'

        if parsedURL.scheme != "http":
            print("Include http:// in the url!")
            sys.exit(1)

        request.append(f"POST {path} HTTP/1.1")

        request.append(f"Host: {parsedURL.hostname}")

        request.append("Accept: */*; charset=utf-8")

        request.append("Connection: close")

        if args is not None:
            l = []
            for k in args:
                l.append(f"{k}={args[k]}")
            q = "&".join(l)


            if parsedURL.query != "":
                q += '&' + parsedURL.query

            request.append("Content-Type: application/x-www-form-urlencoded")
            request.append(f"Content-Length: {len(q)}")
            request.append("")
            request.append(q)
        else:
            if parsedURL.query != "":
                request.append("Content-Type: application/x-www-form-urlencoded")
                q = parsedURL.query
                request.append(f"Content-Length: {len(q)}")
                request.append("")
                request.append(q)
            else:
                request.append("Content-Type: application/x-www-form-urlencoded")
                request.append(f"Content-Length: {0}")            

        data = "\r\n".join(request)
        data += "\r\n\r\n"


        host = parsedURL.hostname
        port = 80
        try:
            port = parsedURL.port
            if port is None:
                port = 80
        except ValueError:
            port = 80


        self.connect(host, port)
        self.sendall(data)
        response = self.recvall(self.socket)
        self.close()

        responseForUser = response

        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    print(sys.argv)
    if (len(sys.argv) <= 2):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 4):
        args = dict(json.loads(sys.argv[3]))
        res = client.command( sys.argv[2], sys.argv[1], args )
        print(responseForUser)
    else:
        res = client.command( sys.argv[2] ) 
        print(responseForUser)

