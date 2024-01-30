import logging
import os
import json
import azure.functions as func
from azure.cosmos import CosmosClient

cosmosproxy = CosmosClient.from_connection_string(os.environ["AzureCosmosDBConnectionString"])
databaseproxy = cosmosproxy.get_database_client(os.environ["Database"])
clientproxy = databaseproxy.get_container_client(os.environ["PlayerContainer"])
def main(req: func.HttpRequest) -> func.HttpResponse:
    input = req.get_json()
    logging.info('leaderboard request incoming with k = {}'.format(input["top"]))
    query = 'SELECT c.username, c.games_played, c.total_score FROM c ORDER BY c.total_score DESC, c.games_played ASC, c.username ASC'
    
    logging.info(f" This is the query {query}")
    players = clientproxy.query_items(
        query=query,
        
        enable_cross_partition_query=True
    )
    output = []
    
    k = input["top"]
    for item in players:
        if k==0:
            break
        output.append(item)
        k -= 1
    return func.HttpResponse(body=json.dumps(output),mimetype="application/json")



   
