====================================================================
:mod:`base_ui` -- Base para todas las interfaces gráficas de Turpial
====================================================================

.. currentmodule:: turpial.ui.base_ui

.. autoclass:: BaseGui()

:class:`BaseGui` methods
------------------------

.. automethod:: BaseGui.__init__
.. automethod:: BaseGui.open_url
.. automethod:: BaseGui.avatar_info_from_url
.. automethod:: BaseGui.current_avatar_path
.. automethod:: BaseGui.parse_tweet
.. automethod:: BaseGui.after_destroy
.. automethod:: BaseGui.read_config
.. automethod:: BaseGui.read_global_config
.. automethod:: BaseGui.save_config
.. automethod:: BaseGui.save_global_config
.. automethod:: BaseGui.request_signin
.. automethod:: BaseGui.request_oauth
.. automethod:: BaseGui.request_auth_token
.. automethod:: BaseGui.request_signout
.. automethod:: BaseGui.request_user_profile
.. automethod:: BaseGui.request_user_avatar
.. automethod:: BaseGui.request_retweet
.. automethod:: BaseGui.request_fav
.. automethod:: BaseGui.request_unfav
.. automethod:: BaseGui.request_mute
.. automethod:: BaseGui.request_unmute
.. automethod:: BaseGui.request_follow
.. automethod:: BaseGui.request_unfollow
.. automethod:: BaseGui.request_direct
.. automethod:: BaseGui.request_destroy_status
.. automethod:: BaseGui.request_short_url
.. automethod:: BaseGui.request_upload_pic
.. automethod:: BaseGui.request_update_status
.. automethod:: BaseGui.request_update_profile
.. automethod:: BaseGui.request_search_topic
.. automethod:: BaseGui.request_search_people
.. automethod:: BaseGui.request_trends
.. automethod:: BaseGui.request_popup_info
.. automethod:: BaseGui.request_conversation
.. automethod:: BaseGui.request_muted_list
.. automethod:: BaseGui.request_update_muted
.. automethod:: BaseGui.request_destroy_direct
.. automethod:: BaseGui.download_timeline
.. automethod:: BaseGui.download_replies
.. automethod:: BaseGui.download_directs
.. automethod:: BaseGui.download_rates
.. automethod:: BaseGui.download_favorites
.. automethod:: BaseGui.resize_avatar
.. automethod:: BaseGui.main_loop
.. automethod:: BaseGui.show_login
.. automethod:: BaseGui.show_main
.. automethod:: BaseGui.show_oauth_pin_request
.. automethod:: BaseGui.cancel_login
.. automethod:: BaseGui.start_updating_timeline
.. automethod:: BaseGui.start_updating_replies
.. automethod:: BaseGui.start_updating_directs
.. automethod:: BaseGui.start_search
.. automethod:: BaseGui.update_tweet
.. automethod:: BaseGui.update_timeline
.. automethod:: BaseGui.update_replies
.. automethod:: BaseGui.update_directs
.. automethod:: BaseGui.update_favorites
.. automethod:: BaseGui.update_rate_limits
.. automethod:: BaseGui.update_follow
.. automethod:: BaseGui.update_user_avatar
.. automethod:: BaseGui.update_user_profile
.. automethod:: BaseGui.update_trends
.. automethod:: BaseGui.update_search_topics
.. automethod:: BaseGui.update_friends
.. automethod:: BaseGui.update_in_reply_to
.. automethod:: BaseGui.update_conversation
.. automethod:: BaseGui.tweet_changed
.. automethod:: BaseGui.tweet_done
.. automethod:: BaseGui.update_config
