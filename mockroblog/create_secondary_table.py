import boto3


def create_secondary_table(dynamodb=None):
    c = boto3.client("dynamodb", endpoint_url="http://localhost:8000")

    table = c.update_table(
        TableName="messages",
        # Any attributes used in your new global secondary index must be declared in AttributeDefinitions
        AttributeDefinitions=[
            {"AttributeName": "receiver", "AttributeType": "S"},
        ],
        # This is where you add, update, or delete any global secondary indexes on your table.
        GlobalSecondaryIndexUpdates=[
            {
                "Create": {
                    # You need to name your index and specifically refer to it when using it for queries.
                    "IndexName": "receiver-index",
                    # Like the table itself, you need to specify the key schema for an index.
                    # For a global secondary index, you can use a simple or composite key schema.
                    "KeySchema": [
                        {"AttributeName": "receiver", "KeyType": "HASH"},
                        {"AttributeName": "timestamp", "KeyType": "RANGE"},
                    ],
                    # You can choose to copy only specific attributes from the original item into the index.
                    # You might want to copy only a few attributes to save space.
                    "Projection": {"ProjectionType": "ALL"},
                    # Global secondary indexes have read and write capacity separate from the underlying table.
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5,
                    },
                }
            }
        ],
    )

    return table


if __name__ == "__main__":
    table = create_secondary_table()
    print("Secondary table status:", table["TableDescription"]["TableStatus"])