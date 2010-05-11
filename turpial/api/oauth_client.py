import httplib
import urllib2
import oauth as oauth

SERVER = 'twitter.com'
PORT = 80

REQUEST_TOKEN_URL = '%s/oauth/request_token'
ACCESS_TOKEN_URL = '%s/oauth/access_token'
AUTHORIZATION_URL = '%s/oauth/authorize'

class TurpialAuthClient(oauth.OAuthClient):

    def __init__(self, server=SERVER, port=httplib.HTTP_PORT, 
        request_token_url=REQUEST_TOKEN_URL, access_token_url=ACCESS_TOKEN_URL, 
        authorization_url=AUTHORIZATION_URL, api_url='http://twitter.com'):
            
        self.server = server
        self.port = port
        self.request_token_url = request_token_url % api_url
        self.access_token_url = access_token_url % api_url
        self.authorization_url = authorization_url % api_url
        #self.connection = httplib.HTTPConnection("%s:%d" % (self.server, self.port))
    
    def fetch_request_token(self, oauth_request):
        #connection = httplib.HTTPConnection("%s:%d" % (self.server, self.port))
        #connection.request(oauth_request.http_method, self.request_token_url, headers=oauth_request.to_header()) 
        #response = connection.getresponse()
        req = urllib2.Request(self.request_token_url, headers=oauth_request.to_header())
        response = urllib2.urlopen(req)
        return oauth.OAuthToken.from_string(response.read())

    def fetch_access_token(self, oauth_request):
        #connection = httplib.HTTPConnection("%s:%d" % (self.server, self.port))
        #connection.request(oauth_request.http_method, self.access_token_url, headers=oauth_request.to_header()) 
        #response = connection.getresponse()
        req = urllib2.Request(self.access_token_url, headers=oauth_request.to_header())
        response = urllib2.urlopen(req)
        return oauth.OAuthToken.from_string(response.read())

    def authorize_token(self, oauth_request):
        #connection = httplib.HTTPConnection("%s:%d" % (self.server, self.port))
        #connection.request(oauth_request.http_method, oauth_request.to_url()) 
        #response = connection.getresponse()
        req = urllib2.Request(oauth_request.to_url())
        response = urllib2.urlopen(req)
        return response.read()

    def access_resource(self, oauth_request, uri, method):
        if method == 'POST':
            headers = {'Content-Type' :'application/x-www-form-urlencoded'}
            body=oauth_request.to_postdata()
            url = uri
        else:
            headers = {}
            body = None
            url = oauth_request.to_url()
        
        req = urllib2.Request(url, body, headers)
        response = urllib2.urlopen(req)
        return response.read()
        
