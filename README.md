
select Read and write and Direct message
Read Tweets and profile information, read and post Direct messages

select native app

callback url https://\<detaappname\>.deta.app/twit/auth_user


## Adding intentful list manager.
- This will be designed such that the there would be a column in the detaspace
Base which describes the target state of the list members.
- Then there would be a periodic job that looks at if the target and the current
state are the same or not and tries to insert the members in the list.
- Since the twitter APIs are rate limited they can't be accessed every single
time when we need to lookup something. It's more like if we do lookup everytime
then we endup in rate limited state.
- So the APIs that we will be exposing will only to edit the target state of the
lists.
- Even the following_list idea that is partially implemented today will be
implemented in the same intentful way described above.