import logging
import os 
import json
from azure.cosmos import CosmosClient
import azure.functions as func

mycosmos = CosmosClient.from_connection_string(os.environ["AzureCosmosDBConnectionString"])
databaseproxy = mycosmos.get_database_client(os.environ["Database"])
promptproxy = databaseproxy.get_container_client(os.environ["PromptContainer"])
def main(req: func.HttpRequest) -> func.HttpResponse:
    input = req.get_json()
    logging.info('this is input {}'.format(input))
    output = []

    for player in input["players"]:
        for doc in promptproxy.read_all_items():
            if doc["username"] == player :
                for text in doc["texts"]:
                    if text["language"] == input["language"]:
                        output.append({"id":doc["id"],"text":text["text"],"username":doc["username"]})
    return func.HttpResponse(body=json.dumps(output),mimetype="application/json")

                

    
