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
    logging.info('Hold on, we have received a request: {}'.format(input))
    deletecount2 = 0  # Initialize the counter here
    word = input["word"]

    if "player" in input:
        deletecount = 0
        for doc in promptproxy.read_all_items():
            if doc["username"] == input["player"]:
                logging.info("Starting to delete for doc with username {}".format(doc["username"]))
                promptproxy.delete_item(item=doc, partition_key=doc["username"])
                deletecount += 1
        return func.HttpResponse(
            body=json.dumps({"result": True, "msg": "{} prompts deleted".format(deletecount)}),
            mimetype="application/json"
        )
    
    if "word" in input:
        for doc in promptproxy.read_all_items():
            for text in doc["texts"]:
                texttodelete = text["text"]
                if f" {word} " in f" {texttodelete} ":
                    promptproxy.delete_item(item=doc,partition_key=doc["username"])
                    deletecount2 +=1

        
        
        return func.HttpResponse(
            body=json.dumps({"result": True, "msg": "{} prompts deleted".format(deletecount2)}),
            mimetype="application/json"
        )
    else:
        return func.HttpResponse(
            body=json.dumps({"result": False, "msg": "Error: No prompts deleted"}),
            mimetype="application/json"
        )
