import logging
import json
import os 
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
import azure.functions as func

from shared_code.player import Player

mycosmos = CosmosClient.from_connection_string(os.environ["AzureCosmosDBConnectionString"])
databaseproxy = mycosmos.get_database_client(os.environ["Database"])
mycosmosproxy = databaseproxy.get_container_client(os.environ["PlayerContainer"])

def main(req: func.HttpRequest) -> func.HttpResponse:
    request = req.get_json()
    logging.info('hold on we got a request to register user {}'.format(request))
    player = Player("username","12345678910")
    try:
        player.input_from_dict(request)
    except ValueError:
        return  func.HttpResponse(body=json.dumps({{"result": False, "msg": "json is not of form player"  }}),mimetype="application/json")
    try:
        player.is_valid()
        
    except ValueError:
        if len(request["username"]) < 4 or len(request["username"]) > 14:
            return func.HttpResponse(body=json.dumps({"result": False, "msg": "Username less than 4 characters or more than 14 characters"  }),mimetype="application/json")
        else:
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "Password less than 10 characters or more than 20 characters"  }),mimetype="application/json")
    cont = True
    for doc in mycosmosproxy.read_all_items():
        if doc["username"] == request["username"]:
            return func.HttpResponse(body=json.dumps({"result": False, "msg": "Username already exists" }),mimetype="application/json")

    try:
        mycosmosproxy.create_item(player.to_dict(),enable_automatic_id_generation=True)
        return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),mimetype="application/json")
    except Exception as ex:
         return func.HttpResponse(body=json.dumps({"result": False, "msg": "something ba happened with the server" }),mimetype="application/json")
# TODO need to add more checks to make sure a password is being entered or maybe not just check later 



    
