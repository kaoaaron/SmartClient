# SmartClient
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

Files:
SmartClient.py
readme.txt

Adknowledgements: 
This project was done as part of the CSC 361 - Computer Communications & Networks class from the University of Victoria in Spring 2018 taught by Dr. Kui Wu.
Thanks to Matthias Friedrich's Blog for providing a nice approach to detecting HTTP 2.0
Link: https://blog.mafr.de/2016/08/27/detecting-http2-support/

Requirements:
Python 3.5 and up is required to execut the program. This is because ALPN was only first introduced in Python 3.5.

How to Run Program:
To run the program, only one parameter can be included. A command, such as the following is valid

python3 SmartClient.py google.ca

Invalid commands include the following

python3 SmartClient.py
python3 SmartClient.py google.ca bananarepublic.com

Status Codes:
The following status codes are checked for in the program
200, 301, 302, 400, 404, 505
