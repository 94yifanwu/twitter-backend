.PHONY: all clean

all: create_table load_data create_secondary_table users timelines load_redis_data


create_table:
	python3 ./init_data/create_table.py
load_data:
	python3 ./init_data/dynamo_load_data.py
create_secondary_table:
	python3 ./init_data/create_secondary_table.py
users: ./init_data/users.sql
	sqlite3 ./init_data/users.db < ./init_data/users.sql
timelines: ./init_data/timelines.sql
	sqlite3 ./init_data/timelines.db < ./init_data/timelines.sql
load_redis_data:
	python3 init_data/redis_load_data.py 

clean:
	rm -f ./init_data/users.db ./init_data/timelines.db
	aws dynamodb delete-table   --table-name messages  --endpoint-url http://localhost:8000  > ./init_data/delete_table_log.txt
	redis-cli flushall
