.PHONY: all clean

all: create_table load_data create_secondary_table users.db timelines.db 

create_table:
	python ./mockroblog/create_table.py
load_data:
	python ./mockroblog/load_data.py
create_secondary_table:
	python ./mockroblog/create_secondary_table.py
users.db: ./mockroblog/users.sql
	sqlite3 ./mockroblog/users.db < ./mockroblog/users.sql
timelines.db: ./mockroblog/timelines.sql
	sqlite3 ./mockroblog/timelines.db < ./mockroblog/timelines.sql

clean:
	rm -f ./mockroblog/users.db ./mockroblog/timelines.db
	aws dynamodb delete-table   --table-name messages  --endpoint-url http://localhost:8000  > ./mockroblog/delete_table_log.txt
	
