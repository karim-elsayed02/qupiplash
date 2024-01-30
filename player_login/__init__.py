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
    logging.info('Hold up we got a request to log in this user {}'.format(input))
    try:
        for doc in clientproxy.read_all_items():
            logging.info("we are inside the for loop")
            if doc["username"] == input["username"] and doc["password"] == input["password"]:
                logging.info("checking this user now {}".format(doc["username"]))
                return func.HttpResponse(body = json.dumps({"result": True , "msg" : "OK"}),mimetype="application/json")
                
        return func.HttpResponse(body = json.dumps({"result": False , "msg": "Username or password incorrect"}),mimetype="application/json")
    except Exception:
        logging.info("some error oh no ")

