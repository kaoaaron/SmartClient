'''
CSC 361 Assignment 1
Author: Aaron Kao
---------------------
Purpose:
This program exists in order to determine
1) whether or not a web server supports HTTPS
2) the newest HTTP version that the webserver supports (HTTP 1.0, HTTP 1.1, or HTTP 2.0)
3) the name, key, and domain name of cookies that the web server uses
'''

##
##LIBRARY IMPORTS
##

import socket
import ssl
import re
import sys

##
##Check for SSL Support
##
##How it works
##1)check if a 200 message is received. If good, SSL supported
##2)if 302 or 301 is obtained, determine if its redirect is http or https and follow until a 200 is obtained
##

if(len(sys.argv) != 2):
    print("Invalid Parameters. Please make sure to only enter 1 additional argument\n")
    sys.exit()

flag = 0; #flag to determine whether or not connect and sendall are successful. changes to 1 if at some point becomes unsucessful

socket.setdefaulttimeout(10) #sets timeout to 10 seconds

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0, None) #opens socket for IPv4 with TCP


host, port = sys.argv[1], 443 #port 443 specifies SSL

try:
    ip = socket.gethostbyname(host) #converts URL to IP. Note: not necessary on client-side
except socket.gaierror:
    print("URL does not exist")
    sys.exit()


request = "GET / HTTP/1.1\r\nHost: "+ host + "\r\nUser-Agent: curl/7.35.0" + "\r\n\r\n" #HTTP request

sock = ssl.wrap_socket(sock, server_side=False, ssl_version=ssl.PROTOCOL_SSLv23) #enables SSL

try:
    sock.connect((ip, port)) #connect to remote socket at address
    sock.sendall(request.encode()) #send HTTP request
except (ssl.SSLError,socket.error,socket.timeout,socket.gaierror,socket.timeout,ssl.CertificateError):
    flag = 1;

reply = sock.recv(2500) #receives reply with buffer as paramater

replyDecoded = reply.decode() #converts reply back to byte string

#if 302 or 301 status code, check for redirection
while(re.match("HTTP\/\d\.\d (302|301)", replyDecoded)):
    temp = re.search(".*Location: (http\w*)\.*", replyDecoded) #assists in finding http or https in redirection

    sock.close()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0, None)
    
    #if URL contains 'https', URL exists
    if(temp.group(1) == "https"):
        port = 443
        sock = ssl.wrap_socket(sock, server_side=False, ssl_version=ssl.PROTOCOL_SSLv23)
        temp = re.search(".*Location: http\w*:\/\/([^\/|\n\r]*)", replyDecoded) #get website domain with TLD
        host = temp.group(1)
        #if host ends with /, strip it
        if(host.endswith("/")):
            host = host.rstrip("/")
        ip = socket.gethostbyname(host)
        
        filenamematch = ".*Location: http\w*:\/\/[^\/|\n\r]*\/([^\n\r]*)"
        searchflag = re.search(filenamematch, replyDecoded)
        #if filename exists; such as not root
        if(searchflag):
            filenamesearch = re.search(filenamematch, replyDecoded)
            filename = filenamesearch.group(1)
        #defaults to / if not filename exists
        else:
            filename = "/"
        
        request = "GET /" + filename + " HTTP/1.1\r\nHost: "+ host + "\r\n\r\n"
        
        try:
            sock.connect((ip, port))
            sock.sendall(request.encode())
        except (ssl.SSLError,socket.error,socket.timeout,socket.gaierror,socket.timeout,ssl.CertificateError):
            flag = 1;
            
        reply = sock.recv(2500)
        replyDecoded = reply.decode()
    #if URL has 'http', URL exists
    elif(temp.group(1) == "http"):
        temp = re.search(".*Location: http\w*:\/\/([^\s]*)", replyDecoded)
        host = temp.group(1)
        #if host ends with /, strip it
        if(host.endswith("/")):
            host = host.rstrip("/")

        ip = socket.gethostbyname(host)
        filenamematch = ".*Location: http\w*:\/\/[^\/|\n\r]*\/([^\n\r]*)"
        searchFlag = re.search(filenamematch, replyDecoded)
        #if filename exists; such as not root
        if(searchFlag):
            filenamesearch = re.search(filenamematch, replyDecoded)
            filename = filenamesearch.group(1)
        #defaults to / if not filename exists
        else:
            filename = "/"
        port = 80
        request = "GET /" + filename + " HTTP/1.1\r\nHost: "+ host + "\r\nUser-Agent: curl/7.35.0" + "\r\n\r\n"
        try:
            sock.connect((ip, port))
            sock.sendall(request.encode())
        except (ssl.SSLError,socket.error,socket.timeout,socket.gaierror,socket.timeout,ssl.CertificateError):
            flag = 1;
        reply = sock.recv(2500)
        replyDecoded = reply.decode()

#if no errors in connect and sendall
if(flag != 1):
#if 200 code is returned, SSL is supported
    if(re.match(".*(200)", replyDecoded)):
        if(port == 443):
            print("SSL Support: Yes")
        elif(port == 80):
            print("SSL Support: No")
    #if 302 or 301 is returned, check for SSL support
    elif(re.match(".*(404)", replyDecoded)):
        print("SSL Support: Yes")
    elif(re.match(".*(505)", replyDecoded)):
        print("SSL Support: Yes")
    else:
        print("SSL Support: Cannot be determined")
#if error in connect or sendall
else:
    print("*Connect or Sendall Failed.\nSSL Support: No")
    
#
## Check HTTP Version 
## HTTP 2.0, HTTP 1.1, or HTTP 1.0
#

ctx = ssl.create_default_context()
ctx.set_alpn_protocols(["h2", "spdy/3", "http/1.1"])

sock = ctx.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=host)

try:
    sock.connect((host, port))
except (ssl.SSLError,socket.error,socket.timeout,socket.gaierror,socket.timeout,ssl.CertificateError):
    pass

if(sock.selected_alpn_protocol() == "h2"):
    print("Latest Supported HTTP Version: HTTP 2.0")
elif(re.match("HTTP\/\d\.\d 400", replyDecoded)):
    print("Latest Supported HTTP Version: Can't be determined")
else:
    if(re.match("HTTP\/(1.1)", replyDecoded)):
        print("Latest Supported HTTP Version: HTTP 1.1")
    elif(re.match("HTTP\/(1.0)", replyDecoded)):
        print("Latest Supported HTTP Version: HTTP 1.0")
    else:
        print("Latest Supported HTTP Version: Cannot be determined")
    
#
## Find Cookies
## Lists the name, token, and domain
#

print("List of Cookies: ")

cookies = re.findall("Set-Cookie: ([^\r\n]*)",replyDecoded) #grabs all lines that have Set-Cookie as starter

count = 0;
#if there are cookies
if(cookies):
    #for each cookie, print out name, token, and domain
    for x in cookies:
        print("Name: -")
        cookieKey = re.search("[^=]*", cookies[count])
        cookieToken = re.search("=([^;]*)",cookies[count])
        cookieDomain = re.search("domain=([^\r\n| ]*)",cookies[count])
        if(cookieKey):
            print("Key: " + cookieKey.group())
        else:
            print("Key: Cookie key not found")
        if(cookieToken):
            print("Token: " + cookieToken.group(1))
        else:
            print("Token: Token not found")
        if(cookieDomain):
            print("Domain: " + cookieDomain.group(1))
        else:
            print("Domain: " + host + " (domain not found from cookie info. grabbed from host instead)")

        print("\n")
        count = count+1
#else no cookies found
else:
    print("No cookies found")

sock.close()
