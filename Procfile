gateway: python3 -m bottle --bind=localhost:$PORT --debug --reload gateway
users: sandman2ctl -p $PORT sqlite+pysqlite:///init_data/users.db
timelines: sandman2ctl -p $PORT sqlite+pysqlite:///init_data/timelines.db
user-queries: datasette -p $PORT --reload init_data/users.db
imeline-queries: datasette -p $PORT --reload init_data/timelines.db
direct-messages: python3 -m bottle --bind=localhost:$PORT --debug --reload direct_message 
search-engine: python3 -m bottle --bind=localhost:$PORT --debug --reload search_engine
dynamoDB: java -Djava.library.path=./dynamodb_local/DynamoDBLocal_lib -jar ./dynamodb_local/DynamoDBLocal.jar -sharedDb
redis: redis-server --port 6379
message-queue: python3 -m bottle --bind=localhost:$PORT --debug --reload message_queue
