import logging
import os
import json
import azure.functions as func
from azure.cosmos import CosmosClient
from shared_code.player import Player



mycosmos = CosmosClient.from_connection_string(os.environ["AzureCosmosDBConnectionString"])
databaseproxy = mycosmos.get_database_client(os.environ["Database"])
mycosmosproxy = databaseproxy.get_container_client(os.environ["PlayerContainer"])

def main(req: func.HttpRequest) -> func.HttpResponse:
    input = req.get_json()
    logging.info('hold on we got a request from {}'.format(input))
    query = "SELECT * FROM c WHERE c.username = @username"
    parameters = [
    {"name": "@username", "value": input["username"]},
    
]
    result = list(mycosmosproxy.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    if result:
        document = result[0]  # Assuming there's only one matching document
        # Modify the document's attributes as needed
        document['games_played'] = document.get('games_played',0) + input.get("add_to_games_played",1)
        document['total_score'] = document.get('total_score',0) + input.get("add_to_score",1)
        logging.info("the input number is {}".format(input.get("add_to_games_played",1)))
        logging.info("the new value for document is {}".format(document["games_played"]))
        # Update the document in the container
        
        mycosmosproxy.upsert_item(document)
        logging.info("Document updated successfully")
        return func.HttpResponse(body =json.dumps({"result" : True, "msg": "OK" }),mimetype="application/json")
        
    else:
         print("Document not found")
         return func.HttpResponse(body =json.dumps({"result": False, "msg": "Player does not exist" }),mimetype="application/json")



    
