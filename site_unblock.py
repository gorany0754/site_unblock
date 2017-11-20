import os,sys,thread,socket

MAX_QUEUE = 20          # Max number of connection
MAX_PKT_SIZE = 4096     # Max size of packet

def main():

    # Usage : python site_unblock.py
    
    port = 8080
    host = ''

    try:
        # create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind host and port
        s.bind((host, port))

        # listenning
        s.listen(MAX_QUEUE)
    
    except socket.error, (value, message):
        if s:
            s.close()
        print "Fail to open socket"
        sys.exit(1)

    # connect with web client 
    while 1:
        conn, client_addr = s.accept()

        # thread to handle web client and end server
        thread.start_new_thread(proxy_thread, (conn, client_addr))
        
    s.close()

def proxy_thread(conn, client_addr):

    # get request from web browser
    request = conn.recv()

    # split first line 
    line = request.split('\n')[0]

    # get url
    url = line.split(' ')[1]
    
    # find the webserver
    http_pos = url.find("://")          # find pos of ://
    if (http_pos==-1):
        webserver = url
    else:
        webserver = url[(http_pos+3):]       # cut off http://

    try:
        # create a socket to connect to the end server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect end server with port 80
        s.connect((webserver, 80))
        # put dummy behind of request
        dummyRequest = 'GET / HTTP/1.1\r\nHost: test.gilgil.net\r\n\r\n'
        request= dummyRequest + request
        # send request to end server
        s.send(request)         
        
        while 1:
            # receive data from end server
            data = s.recv()
            # if 404 data, ignore it
            if data.find('HTTP/1.1 404 Not Found') > 0:
                data = data[1:]
                # find 200 OK data
                dummy_end= data.find('HTTP/1.1 200 OK')
                data = data[dummy_end:]

            if (len(data) > 0):
                # send to browser
                conn.send(data)
            else:
                break
        s.close()
        conn.close()
    except socket.error, (value, message):
        s.close()
        conn.close()
        sys.exit(1)

    
if __name__ == '__main__':
    main()
