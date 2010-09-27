#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# pythonTweetPhoto - A library that provides a python interface to the TweetPhoto API.

# Copyright (c) 2010/2009, Marcel Caraciolo
# caraciol@gmail.com
# twitter: marcelcaraciolo

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the author nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

__author__ = 'caraciol@gmail.com'
__version__ = '0.2'



import httplib, mimetypes
import urllib, urlparse, base64
import simplejson
from xml.dom import minidom as xml

try:
	import cStringIO as StringIO
except ImportError:
	import StringIO

CHARACTER_LIMIT = 200

VOTE_STATUSES = {200:"Vote worked and counted", 401: "Invalid Credentials",
				  409:"User has already voted for that photo", 404:"Photo not found",
				  500: "Internal Error"}
				
COMMENT_STATUSES = {404: "Comment not found", 200: "Comment sucessfully removed"}

class TweetPhotoError(Exception):
	""" Base class for TweetPhoto errors """
	
	@property
	def message(self):
		"""Returns the first argument used to construct this error """
		return self.args[0]
			


			
class TweetPhotoApi(object):
	""" A python interface into the TweetPhoto API 
	
	
	Example usage:
		
		To create a instance of TweetPhotoApi.Api class,  with  authentication
			>>> import pyTweetPhoto
			>>> api = pyTweetPhoto.TweetPhotoApi(username='twitter user', password='twitter pass', api_key='TweetPhoto API Key')'
			
		
		To fecth the details of photo
			>>> photoDetails = api.GetPhotoDetails(photo_id=92922)
			>>> print photoDetails
		
		To upload a photo to TweetPhoto
			>>> status = api.Upload(api.Upload(fileName='FILE_PATH',
			                    message='This is a new photo! max: 200 characters', tags='tag1,tag2,tag3',
			                        geoLocation='lat,long',post_to_twitter=True))
		
		
		There are many other methods, including:

		>>> api.CheckInPhoto(photo_id)
		>>> api.RemoveComment(photo_id,comment_id)
		>>> api.VoteThumbsDown(photo_id)
		>>> api.VoteThumbsUp(photo_id)
		>>> api.RemoveFavoritePhoto(photo_id)
		>>> api.FavoritePhoto(photo_id,post_to_twitter)
		>>> api.AddComment(photo_id,comment_id)
			...
	
	"""
		
	def __init__(self,username=None,password=None,apikey=None):
		
		'''Instantiate a new twitter.Api object.

	  	Args:
			username: the tweetphoto username. (In this case it can be the twitter username).
			password: the tweetphoto password. (In this case it can be the twitter password).
			apikey: the tweetphoto API key. (It can be acquired at http://tweetphoto.com/developer)
			
		'''
		self._urllib = urllib
		self._InitializeRequestHeaders()
		self._InitializeUserAgent()
		self._InitializeDefaultParameters()
		self.SetCredentials(username,password,apikey)

	def SetCredentials(self,username=None,password=None,apikey=None):
		""" Set the username, password and apiKey  for this instance
		
		Args:
			username: the tweetphoto username. (In this case it can be the twitter username).
			password: the tweetphoto password. (In this case it can be the twitter password).
			apikey: the tweetphoto API key. (It can be acquired at http://tweetphoto.com/developer)
		"""
		self._username = username
		self._password = password
		self._apikey = apikey
	
	def ClearCredentials(self):
		""" Clear the username and password for this instance
		"""
		self._username = None
		self._password = None
		self._apikey = None
		
	def _InitializeRequestHeaders(self):	
		self._request_headers = {}
	
	def _InitializeUserAgent(self):
		user_agent = 'Python-urllib/%s (python-tweetphoto/%s)' % \
					(self._urllib.__version__, __version__)

		self.SetUserAgent(user_agent)
		
	def _InitializeDefaultParameters(self):
		self._default_params = {}
		
		
	def GetFileData(self,image=None,fileName=None):
		'''
			Method to get the image content in bytes
			Args:
				image: the image content in bytes
				fileName = the image file path
			Return:
				The image content in bytes
		'''
		if image is not None:
			try:
				filedata = StringIO.StringIO(image)
			except Exception,e:
				raise TweetPhotoError('Problems in reading the image content')
			if fileName is  None:
				fileName = 'default.jpg' #Creates a default fileName
		else:
			try:
				import Image
			except ImportError:
				filedata = StringIO.StringIO(self._urllib.urlopen(fileName).read())
			else:
				filedata = StringIO.StringIO(self._urllib.urlopen(fileName).read())
				img = Image.open(filedata)
		
		return filedata,fileName
		
		
	def GetContentType(self,fileName):
		""" Returns the image content type
			Args:
				fileName: the file path
		"""
		return mimetypes.guess_type(fileName)[0] or 'image/jpg'
		
	
	def SetUserAgent(self, user_agent):
		""" Override the default user agent
		
		Args:
			user_agent: a string that should be send to the server as the User-agent
		"""
		self._user_agent= user_agent
		
	
	def SignIn(self):
		""" Sign in into the TweetPhoto webservice. It's a privileged operation
			and thus the username/password is required
			
			Before use SignIn, make sure that your credentials are passed to the API.
			
			Ps: By the default it uses the Basic Auth SignIn (For now only twitter users)
			
		Returns:
			A pyTweetPhoto.User instance representing the user authenticated.
		"""
		
		if not self._username or not self._password:
			raise TweetPhotoError('the pyTweetPhoto.TweetPhotoApi instance must be authenticated.')
		
		url = 'http://tweetphotoapi.com/api/tpapi.svc/json/signin'
		
		
		self._request_headers = {}
		
		self._request_headers['TPAPI'] = self._username + ',' + self._password
		
		json  = self._FetchUrl(url)
		
		if 'Request Error' in json:
			raise TweetPhotoError('(403) Invalid Credentials')
		
		data  = simplejson.loads(json)
		self._CheckForTweetPhotoError(data)
		return data


	def CheckInPhoto(self,user_id=None,photo_id=None):
		
		""" Remove a user favorite related to photo. This is a privileged operation and need be user
			authenticated. Before using this method it's necessary the TweetPhotoApi.SignIn calling
			procedure.

			Args:
				user_id: must be the user id in the profile
				photo_id: the id of the photo.
		
			Returns:
				The status Code of the response
		"""
		if user_id:
			userId = user_id
		elif self._username and self._password:
			userProfile = self.SignIn()
			userId = userProfile['Id']
		else:
			raise TweetPhotoError('You must have a valid user ID to remove the favorite photo')

		if not photo_id:
			raise TweetPhotoError("You must have a valid photo ID to remove as favorite.")

		url = 'http://tweetphotoapi.com/api/tpapi.svc/json/users/%s/views/%s' % (userId,photo_id)

		self._request_headers = {}

		self._request_headers['TPAPI'] = self._username + ',' + self._password
		
		self._request_headers['content-length'] = str(len(""))

		statusCode,data  = self._FetchUrlPD(url,"POST","")

		if 'Request Error' in data:
			raise TweetPhotoError('(403) Invalid photoID')

		#How to check a flag that the photo has be viewed ?!
		return {'StatusCode': statusCode}
	

	def VoteThumbsDown(self,photo_id=None,post_to_twitter=False):
		""" Allows user to vote for a photo  with a "thumbs up" or "thumbs down" system
			This method is for thumbs up.  This is a privileged operation and need be user
			authenticated. Before using this method it's necessary the TweetPhotoApi.SignIn 
			calling procedure. 

				Args:
					photo_id: the id of the photo
					post_to_twitter: It specifies whether or not to post the vote and a link
						to the photo in the Twitter service

		"""
		if self._username and self._password:
			userProfile = self.SignIn()
		else:
			raise TweetPhotoError('You must have a valid user ID to mark as liked the photo')

		if not photo_id:	
			raise TweetPhotoError("You must have a valid photo ID to mark as liked the photo.")


		url = 'http://tweetphotoapi.com/api/tpapi.svc/json/photos/%s/thumbsdown' %photo_id

		self._request_headers = {}

		self._request_headers['TPAPI'] = self._username + ',' + self._password
		self._request_headers['content-length'] = str(len(""))
		
		self._request_headers['TPPOST'] = str(post_to_twitter)

		statusCode,json  = self._FetchUrlPD(url,"PUT","")

		if 'Request Error' in json:
			raise TweetPhotoError('(403) Invalid photoID')

		#Return the HTTP Status Code and message status dict
		return {'StatusCode': statusCode, 'Message':VOTE_STATUSES[statusCode]}

	
	
	def GetPhotoDetails(self,photo_id=None):
		""" Get all the metadata for a photo, including user comments 
		
			Args:
				photo_id: the id of the photo.
			
			Returns:
				the photo metadata
		
		"""
		if not photo_id:
			raise TweetPhotoError("You must have a valid photo ID to get its details.")
		
		url = 'http://tweetphotoapi.com/api/tpapi.svc/json/photos/%s?gettag=true' %photo_id
		
		json  = self._FetchUrl(url)
		
		if 'Request Error' in json:
			raise TweetPhotoError('(403) Invalid photoID')
		
		data  = simplejson.loads(json)
		self._CheckForTweetPhotoError(data)
		
		return data	
		

	def VoteThumbsUp(self,photo_id=None,post_to_twitter=False):
		""" Allows user to vote for a photo  with a "thumbs up" or "thumbs down" system
			This method is for thumbs up.  This is a privileged operation and need be user
			authenticated. Before using this method it's necessary the TweetPhotoApi.SignIn 
			calling procedure. 
			
				Args:
					photo_id: the id of the photo
					post_to_twitter: It specifies whether or not to post the vote and a link
						to the photo in the Twitter service
				
				Returns:
					The Status code and message status
				
		"""
		if self._username and self._password:
			userProfile = self.SignIn()
		else:
			raise TweetPhotoError('You must have a valid user ID to mark as liked the photo')
		
		if not photo_id:	
			raise TweetPhotoError("You must have a valid photo ID to mark as liked the photo.")

		
		url = 'http://tweetphotoapi.com/api/tpapi.svc/json/photos/%s/thumbsup' %photo_id

		self._request_headers = {}
		
		self._request_headers['TPPOST'] = str(post_to_twitter)

		self._request_headers['TPAPI'] = self._username + ',' + self._password
		self._request_headers['content-length'] = str(len(""))

		statusCode,json  = self._FetchUrlPD(url,"PUT","")
		
		if 'Request Error' in json:
			raise TweetPhotoError('(403) Invalid photoID')

		#Return the HTTP Status Code and message status dict
		return {'StatusCode': statusCode, 'Message':VOTE_STATUSES[statusCode]}
		
			
	def RemoveFavoritePhoto(self,user_id=None,photo_id=None,post_to_twitter=False):
		""" Remove a user favorite related to photo. This is a privileged operation and need be user
			authenticated. Before using this method it's necessary the TweetPhotoApi.SignIn calling
			procedure.

			Args:
				user_id: must be the user id in the profile
				photo_id: the id of the photo.
				post_to_twitter: It specifies whether or not to post the favorite and a link
					to the photo in the Twitter service

			Returns:
				The current status of the favorite photo
		"""
		if user_id:
			userId = user_id
		elif self._username and self._password:
			userProfile = self.SignIn()
			userId = userProfile['Id']
		else:
			raise TweetPhotoError('You must have a valid user ID to remove the favorite photo')

		if not photo_id:
			raise TweetPhotoError("You must have a valid photo ID to remove as favorite.")

		url = 'http://tweetphotoapi.com/api/tpapi.svc/json/users/%s/favorites/%s' % (userId,photo_id)

		self._request_headers = {}

		if post_to_twitter:
			self._request_headers['TPPOST'] = 'True'


		self._request_headers['TPAPI'] = self._username + ',' + self._password

		status_code,json  = self._FetchUrlPD(url,"DELETE")

		if 'Request Error' in json:
			raise TweetPhotoError('(403) Invalid photoID')

		#Request again the URL, now to fetch the current status of the photo (Favorite)
		json  = self._FetchUrl(url)
		data  = simplejson.loads(json)
		self._CheckForTweetPhotoError(data)

		return data
	
	
	def DeletePhoto(self,photo_id=None):
		""" Delete a photo the user has uploaded. This is a privileged operation and need the
			user be authenticated. Before using this method it's necessary the 
			TweetPhotoApi.SignIn calling procedure.
			
			Args:
				photo_id: The unique id of the photo
			
			Returns:
				Returns the status Response of the operation
		"""

		if not self._username or not self._password:
			raise TweetPhotoError('You must have be authenticated to do the delete operation.')
					
		if not photo_id:
			raise TweetPhotoError("You must have a valid photo ID to delete the photo.")

		url = 'http://tweetphotoapi.com/api/tpapi.svc/json/photos/%s' %photo_id
		
		self._request_headers = {}

		self._request_headers['TPAPI'] = self._username + ',' + self._password

		status_code,json  = self._FetchUrlPD(url,"DELETE")
		
		if status_code == 403:
			raise TweetPhotoError("User credentials are invalid")
			
		if status_code == 404:
			raise TweetPhotoError("The photo does not exist")
			
		#Return 200 (Sucessfull)
		return {'StatusCode': status_code, 'Message':"Operation sucessfull"}
		
	
	def FavoritePhoto(self,user_id=None,photo_id=None,post_to_twitter=False):
		""" Add a user favorite related to photo. This is a privileged operation and need be user
			authenticated. Before using this method it's necessary the TweetPhotoApi.SignIn calling
			procedure.
			
			Args:
				user_id: must be the user id in the profile
				photo_id: the id of the photo.
				post_to_twitter: It specifies whether or not to post the favorite and a link
					to the photo in the Twitter service
				
			Returns:
				The current status of the favorite photo
		"""
		
		if user_id:
			userId = user_id
		elif self._username and self._password:
			userProfile = self.SignIn()
			userId = userProfile['Id']
		else:
			raise TweetPhotoError('You must have a valid user ID to add the favorite photo')
		
		if not photo_id:
			raise TweetPhotoError("You must have a valid photo ID to add as favorite.")
		
		url = 'http://tweetphotoapi.com/api/tpapi.svc/json/users/%s/favorites/%s' % (userId,photo_id)
		
		self._request_headers = {}

		if post_to_twitter:
			self._request_headers['TPPOST'] = 'True'

			
		self._request_headers['TPAPI'] = self._username + ',' + self._password

		json  = self._FetchUrl(url,"")
				
		if 'Request Error' in json:
			raise TweetPhotoError('(403) Invalid photoID')
		
		#Request again the URL, now to fetch the current status of the photo (Favorite)
		json  = self._FetchUrl(url)
		data  = simplejson.loads(json)
		self._CheckForTweetPhotoError(data)
		
		return data

	def RemoveComment(self,user_id=None,photo_id=None,comment_id=None):
		""" Delete a comment to a photo. This is a privileged operation and need be user authenticated.
			Before using this method it's necessary the TweetPhotoAPi.SignIn calling procedure.

			Args:
				user_id: must be the user id in the profile
				photo_id: is a valid id for a photo object
				comment_id: the comment that will be deleted from the photo.
			Returns:
				The  statud code response
		"""

		if user_id:
			userId = user_id
		elif self._username and self._password:
			userProfile = self.SignIn()
			userId = userProfile['Id']
		else:
			raise TweetPhotoError('You must have a valid user ID to remove the comment')

		if not photo_id:
			raise TweetPhotoError('You must have a valid photo ID to remove the comment')
		
		if not comment_id:
			raise TweetPhotoError('You must have a valid photo ID to remove the comment')

		url = 'http://tweetphotoapi.com/api/tpapi.svc/json/users/%s/comments/%s/%s' % (userId,photo_id,comment_id)

		self._request_headers = {}
		
		self._request_headers['TPAPI'] = self._username + ',' + self._password

		status_code,json  = self._FetchUrlPD(url,"DELETE")

		if 'Request Error' in json:
			raise TweetPhotoError('(403) Invalid photoID')

		#Return the HTTP Status Code and message status dict
		return {'StatusCode': status_code, 'Message':COMMENT_STATUSES[status_code]}
	
	
	def AddComment(self,user_id=None,photo_id=None,comment=None,post_to_twitter=False):
		""" Add a comment to a photo. This is a privileged operation and need be user authenticated.
			Before using this method it's necessary the TweetPhotoApi.SignIn calling procedure.
			
			Args:
				user_id: must be the user id in the profile
				photo_id: is a valid id for a photo object
				comment: the comment that will be added to the photo.
				post_to_twitter: It specifies whether or not to post the comment and a link
					to the photo in the Twitter service
			Returns:
				The comment  response
		"""
		
		if user_id:
			userId = user_id
		elif self._username and self._password:
			userProfile = self.SignIn()
			userId = userProfile['Id']
		else:
			raise TweetPhotoError('You must have a valid user ID to comment')
	
		if not photo_id:
			raise TweetPhotoError('You must have a valid photo ID to comment')
		
		url = 'http://tweetphotoapi.com/api/tpapi.svc/json/users/%s/comments/%s' % (userId,photo_id)
		
		self._request_headers = {}
		
		if post_to_twitter:
			self._request_headers['TPPOST'] = 'True'
			
		post_data = comment	
				
		self._request_headers['TPAPI'] = self._username + ',' + self._password
		
		json  = self._FetchUrl(url,post_data)

		if 'Request Error' in json:
			raise TweetPhotoError('(403) Invalid photoID or Invalid comment')
		
		data  = simplejson.loads(json)
		self._CheckForTweetPhotoError(data)
		
		return data
		

	def Upload(self,fileName=None,image=None, message=None, tags=None, geoLocation=None,post_to_twitter= False, headers=None):
		""" Upload a photo to TweetPhoto Web Service from the authenticated user 
		
			The pyTweetPhoto.TweetPhotoApi must be authenticated.
			
			Args:
				image: the Image byte stream
				fileName: the Image file path
				message: the message text to be posted with the photo, limited to 200 characters.
				tags: a comma delimited list of tags for the photo in a string (e.g. 'cat,funny,house')
				geoLocation: a string in the format lat,long with the geolocation tag for latitude and longitude
				post_to_twitter: Whether or not to post to twitter
			Return:
				A structured data representing the photo uploaded.
				
		"""
				
		if not self._username or not self._password or not self._apikey:
			raise TweetPhotoError('the pyTweetPhoto.TweetPhotoApi instance must be authenticated.')
		
		#url = 'http://tweetphotoapi.com/api/tpapi.svc/json/upload2'
		url = 'http://api.plixi.com/api/tpapi.svc/upload2'
		
		if not image and not fileName:
			raise TweetPhotoError('There must be some image data or filename to upload the data.')

		
		filedata,fileName = self.GetFileData(image,fileName)
		
		if not filedata and not filename:
			raise TweetPhotoError('Error during the loading of the image content')
		
		filedata = filedata.getvalue()
				
		if message is not None:
			if len(message) > CHARACTER_LIMIT:
				raise TweetPhotoError('Text must be less than or equal to %s characters.' % CHARACTER_LIMIT)
		
				
		#self._request_headers['TPAPI'] = self._username + ',' + self._password
		self._request_headers['TPAPIKEY'] =	self._apikey
		self._request_headers['TPMIMETYPE'] = self.GetContentType(fileName)
		
		if post_to_twitter: #Default value is False
			self._request_headers['TPPOST'] = 'True'

		if message is not None: #Default value is Null
			self._request_headers["TPMSG"] = message
		
		if tags is not None: #Default value is Null
			self._request_headers['TPTAGS'] = tags
		
		if geoLocation is not None: #Default value is Null'
			g = geoLocation.split(',')
			if len(g) != 2:
				raise TweetPhotoError("Problems in parsing the Geolocation data.")
			self._request_headers['TPLAT'] = g[0]
			self._request_headers['TPLONG'] = g[1]
		
		if headers:
			self._request_headers['X-Verify-Credentials-Authorization'] = headers['X-Verify-Credentials-Authorization']
			self._request_headers['X-Auth-Service-Provider'] = headers['X-Auth-Service-Provider']
		
		self._request_headers['content-type'] = 'application/x-www-form-urlencoded'
		self._request_headers['content-length'] = str(len(filedata))
		#print self._request_headers
		data  = self._FetchUpload(url,post_data=filedata)
		#print json
		#data  = simplejson.loads(json)
		self._CheckForTweetPhotoError(data)
		return data
		
		
	def _CheckForTweetPhotoError(self,data):
		""" Raises a Twitter Error if tweetphoto returns a error message.
		
		Args:
			data: a python dict created from TweetPhoto json response.
		
		Raises:
			TweetPhotoError wrapping the tweetphoto error message if one exists.
		
		"""
		if 'Error' in data:
			raise TweetPhotoError('(' + str(data['Error']['ErrorCode']) + ') ' + data['Error']['Message'])
			
			
	def _FetchUpload(self,url,post_data):
		""" Method to upload data using chunked upload of data 
		
			Args:
				url: The upload URL
				post_data: The image content bytes
			
			Return:
				url_data: The url response
		"""
		BLOCKSIZE = 8192
		
		#Create the connection with the server
		(scheme,netloc,path,params,query,fragment) = urlparse.urlparse(url)
		connection = httplib.HTTP(netloc)
		connection.putrequest('POST', '/%s' %path)
		
		#Append the request headers
		for k,v in self._request_headers.items():
			if v is not None:
				connection.putheader(k,v)
		
		connection.endheaders()
		
		#Send the data by chunks of size BLOCKSIZE
		offs = 0
		for i in range(0,len(post_data),BLOCKSIZE):
			offs+=BLOCKSIZE
			connection.send(post_data[i:offs])
		
		#Get the response of the server
		statusCode,statusMsg, headers = connection.getreply()
		url_data = connection.file.read()
		
		#Always return the latest version
		return url_data
		
		
	class _FancyURLopener(urllib.FancyURLopener):
		""" This class handles the basic auth, providing user and password 
			when required by http response codd 401
		"""
		def __init__(self,usr,pwd):
			""" Set user/password for http and call base class constructor
			"""
			urllib.FancyURLopener.__init__(self)
			self.usr = usr
			self.pwd = pwd
		
		
		def prompt_user_passwd(self,host,realm):
			"""
			Basic auth callback
			"""
			return (self.usr, self.pwd)
			
			
	def _FetchUrlPD(self,url,request,data=None):
		""" Fetch a URL method request PUT/DELETE 
			Args:
				url: the url to retrieve
				request: The request method
				data: data to send
			Returns:
				A string containing the body of the response and the response status Code
		"""
		#Create the connection with the server
		(scheme,netloc,path,params,query,fragment) = urlparse.urlparse(url)
		connection = httplib.HTTP(netloc)
		connection.putrequest('%s' %request, '/%s' %path)
		
		#Append the request headers
		for k,v in self._request_headers.items():
			if v is not None:
				connection.putheader(k,v)
		
		connection.endheaders()
		
		if data:
			connection.send(data)
			
		
		#Get the response of the server
		statusCode,statusMsg, headers = connection.getreply()
		url_data = connection.file.read()
		
		#Always return the latest version
		return statusCode,url_data	
	
	
	def _FetchUrl(self, url, post_data = None, parameters = None):
		""" Fetch a URL  method request GET/POST
			Args:
				url: the url to retrieve
				post_data:
					A dict of (str,unicode) key/value pairs. if set, POST will be used.
				parameters:
					a dict whose key/values pair should encoded and added to the query string. [OPTIONAL]

			Returns:
				A string containing the body of the response
		"""
		
		#Build the extra parameters dict
		extra_params = {}
		if self._default_params:
			extra_params.update(self._default_params)
		
		if parameters:
			extra_params.update(parameters)
			
		
		#Add key/value parameters to the query string of the url
		url = self._BuildUrl(url,extra_params=extra_params)
		
		#Get a url opener that can handle basic auth
		opener = self._GetOpener(username=self._username,password=self._password)
			
		#Encode the POST data
		encoded_post_data = self._EncodePostData(post_data)
		
		#Open the URL request
		url_data = opener.open(url,encoded_post_data).read()		
		opener.close()

		#Always return the latest version
		return url_data
		
	
	
	def _EncodePostData(self,post_data):
		""" Return a string in key=value&key=value form
		
		Args:
			post_data:
				A dict of (key,value) tuples.
		
		Returns:
			A URL-encoded string in 'key=value&key=value' form
		
		"""
		if post_data is None:
			return None
		elif type(post_data) == type({}):
			return urllib.urlencode(dict([(k,value) for k,value in post_data.items()]))
		else:
			return post_data
		
	def _EncodeParameters(self,parameters):
		""" Return a string in key=value&key=value form
			
			Value of None are not included in the output string.
			
			Args:
				parameters:
					A dict of (key,value) tuples.
			
			Return:
				a URL-encoded string in 'key=value&key=value' form
		"""
		if parameters is None:
			return None
		else:
			return urllib.urlencode(dict([ (k,value) for k,value in parameters.items() if value is not None]))


	def _GetOpener(self,username=None, password=None):
		if username and password:
			opener = TweetPhotoApi._FancyURLopener(username,password)
		else:
			raise TweetPhotoError("Until now no handler for No-Authenticated access")
		opener.addheaders = self._request_headers.items()
		return opener

	
	def _BuildUrl(self,url,path_elements=None, extra_params=None):
		#Break url into consituent parts
		(scheme,netloc,path,params,query,fragment) = urlparse.urlparse(url)
		
		#Add any additional path elements to the path
		if path_elements:
			#Filter out the path elements that have a value of None
			p = [i for i in path_elements if i]
			if not path.endswith('/'):
				path+='/'
			path += '/'.join(p)
		
		#Add any additional query parameters to the query string
		if extra_params and len(extra_params) > 0:
			extra_query = self._EncodeParameters(extra_params)
			#Add it to the existing query
			if query:
				query += '&' + extra_query
			else:
				query = extra_query
		
		#Return the rebuilt URL
		return urlparse.urlunparse((scheme,netloc,path,params,query,fragment))	
