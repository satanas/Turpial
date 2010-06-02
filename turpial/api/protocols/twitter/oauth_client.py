import urllib
import httplib
import urllib2

SERVER = 'twitter.com'
PORT = 80

REQUEST_TOKEN_URL = '%s/oauth/request_token'
ACCESS_TOKEN_URL = '%s/oauth/access_token'
AUTHORIZATION_URL = '%s/oauth/authorize'

from turpial.api.protocols.twitter import oauth
from turpial.api.protocols.twitter.twitter_globals import CONSUMER_KEY, CONSUMER_SECRET

class TurpialAuthClient(oauth.OAuthClient):

    def __init__(self, server=SERVER, port=httplib.HTTP_PORT, 
        request_token_url=REQUEST_TOKEN_URL, access_token_url=ACCESS_TOKEN_URL, 
        authorization_url=AUTHORIZATION_URL, api_url=None):
        
        if not api_url:
            api_url = 'https://api.twitter.com'
        
        self.server = server
        self.port = port
        self.request_token_url = request_token_url % api_url
        self.access_token_url = access_token_url % api_url
        self.authorization_url = authorization_url % api_url
        
        self.token = None
        self.consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
        self.signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
    
    def fetch_request_token(self, oauth_request):
        req = urllib2.Request(self.request_token_url, headers=oauth_request.to_header())
        response = urllib2.urlopen(req)
        return oauth.OAuthToken.from_string(response.read())
        
    def fetch_access_token(self, oauth_request):
        req = urllib2.Request(self.access_token_url, headers=oauth_request.to_header())
        response = urllib2.urlopen(req)
        self.token = oauth.OAuthToken.from_string(response.read())
        return self.token
        
    def build_access_token(self, key, secret):
        return oauth.OAuthToken(key, secret)
        
    def fetch_xauth_access_token(self, username, password):
        url = self.access_token_url
        request = oauth.OAuthRequest.from_consumer_and_token(
            oauth_consumer=self.consumer,
            http_method='POST', http_url=url,
            parameters = {
                'x_auth_mode': 'client_auth',
                'x_auth_username': username,
                'x_auth_password': password
            }
        )
        request.sign_request(self.signature_method_hmac_sha1, self.consumer, None)

        req = urllib2.Request(url, data=request.to_postdata())
        response = urllib2.urlopen(req)
        self.token = oauth.OAuthToken.from_string(response.read())
        return self.token
        
    def authorize_token(self, oauth_request):
        req = urllib2.Request(oauth_request.to_url())
        response = urllib2.urlopen(req)
        return response.read()
            
    def apply_auth(self, request, params):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
            token=self.token, http_method=request.method, http_url=request.uri, 
            parameters=params)
        oauth_request.sign_request(self.signature_method_hmac_sha1,
            self.consumer, self.token)
        request.headers.update(oauth_request.to_header())
        
    def access_resource(self, uri, method, params):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
            token=self.token, http_method=method, http_url=uri, 
            parameters=params)
        oauth_request.sign_request(self.signature_method_hmac_sha1,
            self.consumer, self.token)
            
        if method == 'POST':
            headers = {'Content-Type' :'application/x-www-form-urlencoded'}
            headers.update(oauth_request.to_header())
            body=oauth_request.to_postdata()
            url = uri
        else:
            headers = {}
            body = None
            url = oauth_request.to_url()
        
        #req = urllib2.Request(url, body, headers)
        req = urllib2.Request(url, data=oauth_request.to_postdata())
        response = urllib2.urlopen(req)
        return response.read()
        
