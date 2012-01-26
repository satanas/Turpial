'''
List of twitter method names that require the use of POST
'''

POST_ACTIONS = [

    # Status Methods
    'update',

    # Direct Message Methods
    'new',

    # Account Methods
    'update_profile_image', 'update_delivery_device', 'update_profile',
    'update_profile_background_image', 'update_profile_colors',
    'update_location', 'end_session',

    # Notification Methods
    'leave', 'follow',

    # Status Methods, Block Methods, Direct Message Methods, 
    # Friendship Methods, Favorite Methods
    'destroy',

    # Block Methods, Friendship Methods, Favorite Methods
    'create',
    
    'retweet',

]

# key and secret granted by the service provider for this consumer application
CONSUMER_KEY = 'j0uEGFlrexq9XE3OuFQBA'
CONSUMER_SECRET = 'hv1ms0FbalCEDoelzMvH8TPadO5jERJk77XVPJ6zoTM'
