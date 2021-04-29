# 449-proj6-bottle-gateway-dynamoDB-redis

This project includes API gateway, load balace, basic authentication for micro blog services. DynamoDB for directly messages services. Redis for inverted index search engine to search posts contents.

---

working on proj6

2.  $ foreman start

3.  go to browser and enter localhost:5000/search/

index(postId, text)
Adds the text of a post identified by postId to the inverted index.
-- provide postID and text string.

search(keyword)
Returns a list of postIds whose text contains keyword.

option 1: use browser and enter: `http://localhost:5000/search-engine/search-any/profavery`
option 2: use terminal `$ http -a ProfAvery:password -v GET 'localhost:5000/search-engine/search/profavery'`

any(keywordList) - OR
Returns a list of postIds whose text contains any of the words in keywordList.

option 1: use browser and enter: `http://localhost:5000/search-engine/search-any/profavery+tuffy`
option 2: use terminal `$ http -a ProfAvery:password -v GET 'localhost:5000/search-engine/search-any/profavery+tuffy'`

all(keywordList) - AND
Returns a list of postIds whose text contains all of the words in keywordList.
option 1: use browser and enter: `http://localhost:5000/search-engine/search-all/profavery+tuffy`
option 2: use terminal `$ http -a ProfAvery:password -v GET 'localhost:5000/search-engine/search-all/profavery+tuffy'`

exclude(includeList, excludeList)
Returns a list of postIds whose text contains any of the words in includeList unless they also contain a word in excludeList.
option 1: use browser and enter: `http://localhost:5000/search-engine/search-exclude/profavery+tuffy/test+one`
option 2: use terminal `$ http -a ProfAvery:password -v GET 'localhost:5000/search-engine/search-exclude/profavery+tuffy/test+one'`

---

# Initialize:

1: `foreman start` or `foreman start -m gateway=1,users=1,timelines=3,user-queries=1,timeline-queries=1,direct-messages=1,search-engine=1,dynamoDB=1,redis=1`

2: `make` (use a separate terminal)

(option: run `make clean` ahead of `make` in case of pre-exist errors)

(Note: `make` creates users.db and timelines.db, create chat_table, create_secondary_table, and load_data to chat_table;

# Authentication:

example of get_feed:

`http -a ProfAvery:password 'localhost:5000/home/ProfAvery'`

example of list Direct Messages username='ProfAvery' receives:

`http -a ProfAvery:password -v GET 'localhost:5000/dm/username/ProfAvery/receiver'`

# Test API

## direct messages

Note: if Authentication is on, 'username' should be the same as 'sender'.

#### sendDirectMessage(inputs)

`http -a ProfAvery:password -v POST localhost:5000/dm/ sender='ProfAvery' receiver='tester' content='this is http POST' quick-replies:='{"1":"red","2":"white","3":"black","4":"yellow"}'`

`http -a ProfAvery:password -v POST localhost:5000/dm/ sender='NotProfAvery' receiver='tester' content='this is http POST' quick-replies:='{"1":"red","2":"white","3":"black","4":"yellow"}'`

(note: this will cause 401, since user != sender)

#### replyToDirectMessage(inputs)

`http -a ProfAvery:password -v POST localhost:5000/dm/ chat_id='tester#0005' is_text='False' sender='ProfAvery' receiver='tester' content='2'`

`http -a ProfAvery:password -v POST localhost:5000/dm/ chat_id='tester#0005' is_text='True' sender='ProfAvery' receiver='tester' content='i want to get green color'`

`http -a ProfAvery:password -v POST localhost:5000/dm/ chat_id='tester#0007' is_text='False' sender='ProfAvery' receiver='tester' content='3'`

(note: this will cause error because the latest message of chat_id='tester#0007' & sender='tester' don not contain quick_replies fields')

#### listDirectMessagesForThe(username)

`http -a ProfAvery:password -v GET 'localhost:5000/dm/username/ProfAvery/receiver'`

#### listRepliesTo(messageId)

`http -a ProfAvery:password -v GET 'localhost:5000/dm/username/ProfAvery/message/0001'`

## users

#### createUser(username, email, password)

`http -a ProfAvery:password -v POST localhost:5000/users/ username=tester email=test@example.com password=testing`

#### authenticateUser(username, password)

`http -a ProfAvery:password -v GET 'localhost:5000/users/?username=ProfAvery&password=password'`

#### addFollower(username, usernameToFollow)

`http -a ProfAvery:password -v POST localhost:5000/followers/ follower_id=4 following_id=2`

#### removeFollower(username, usernameToRemove)

`http -a ProfAvery:password -v DELETE localhost:5000/followers/4`

## timelines

#### getUserTimeline(username)

`http -a ProfAvery:password -v GET 'localhost:5000/posts/?username=ProfAvery&sort=-timestamp'`

#### getPublicTimeline()

`http -a ProfAvery:password -v GET 'localhost:5000/posts/?sort=-timestamp'`

#### getHomeTimeline(username)

`http -a ProfAvery:password -v GET "http://localhost:5000/home/ProfAvery"`

#### postTweet(username, text)

`http -a ProfAvery:password -v POST localhost:5000/posts/ username=tester text='This is a test'`
