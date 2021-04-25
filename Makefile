.PHONY: all clean

#all: create_table load_data create_secondary_table users.db timelines.db 
all: users.db timelines.db 

#create_table:
	python3 ./init_data/create_table.py
#load_data:
	python3 ./init_data/load_data.py
#create_secondary_table:
	python3 ./init_data/create_secondary_table.py
users.db: ./init_data/users.sql
	sqlite3 ./init_data/users.db < ./init_data/users.sql
timelines.db: ./init_data/timelines.sql
	sqlite3 ./init_data/timelines.db < ./init_data/timelines.sql


clean:
	rm -f ./init_data/users.db ./init_data/timelines.db
	aws dynamodb delete-table   --table-name messages  --endpoint-url http://localhost:8000  > ./init_data/delete_table_log.txt
	
