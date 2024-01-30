import logging
from azure.cosmos import CosmosClient
import os
import json
import requests
import azure.functions as func

mycosmos = CosmosClient.from_connection_string(os.environ["AzureCosmosDBConnectionString"])
databaseproxy = mycosmos.get_database_client(os.environ["Database"])
mycosmosproxy = databaseproxy.get_container_client(os.environ["PlayerContainer"])
promptproxy = databaseproxy.get_container_client(os.environ["PromptContainer"])

uri = os.environ["TranslationEndpoint"]
key = os.environ["TranslationKey"]
 # Define the translation URL
translate_url = f"{uri}/translate?api-version=3.0"

# Supported languages
supported_languages = ['en', 'es', 'it', 'sv', 'ru', 'id', 'bg', 'zh-Hans']

# Set up headers for the request
headers = {
    "Ocp-Apim-Subscription-Key": key,
    'Ocp-Apim-Subscription-Region': 'uksouth',
    "Content-Type": "application/json"
}



def main(req: func.HttpRequest) -> func.HttpResponse:
    input = req.get_json()
    logging.info('Python HTTP trigger function processed a request.')
    query = "SELECT * FROM c WHERE c.username = @username"
    parameters = [
    {"name": "@username", "value": input["username"]},
    
]
    result = list(mycosmosproxy.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    if not result:
        return func.HttpResponse(body = json.dumps({"result" : False, "msg": "Player does not exist"}),mimetype="application/json")
    
    if len(input["text"]) < 15 or len(input["text"]) > 80:
        return func.HttpResponse(body = json.dumps({"result": False, "msg": "Prompt less than 15 characters or more than 80 characters"  }),mimetype="application/json") 
     # Detect language using Azure Translator
    detection_data = [
        {
            "text": input["text"]
        }
    ]
    detection_response = requests.post(f"{uri}/detect?api-version=3.0", headers=headers, json=detection_data)
    logging.info(f"Starting detection {detection_response.json()}")
    detection_response.raise_for_status()
    detected_language = detection_response.json()[0]['language']
    if detected_language not in supported_languages or detection_response.json()[0]['score'] < 0.3:
            logging.info("Unsupported language")
            return func.HttpResponse(body=json.dumps({"result": False,"msg": "unsupported language"}), mimetype="application/json")
    to_languages = supported_languages.copy()
    to_languages.remove(detected_language)

    params = {
        "from": detected_language,
        "to": to_languages
    }
    body = [{"text": input["text"]}]
    texts = [{"language": detected_language, "text":input["text"]}]
    translate_url = os.environ['TranslationEndpoint'] + "/translate?api-version=3.0&to=" + "&to=".join(supported_languages)
    request = requests.post(translate_url,headers=headers,json=body)
    response = request.json()
    
    for translation in response[0]['translations']:
        texts.append({"language": translation['to'], "text": translation['text']})

        prompt_doc = {
            "username": input["username"],
            "texts": texts
        }
    promptproxy.create_item(body=prompt_doc, enable_automatic_id_generation=True)

    logging.info("Prompt creation successful")
    
    return func.HttpResponse(body=json.dumps({"result" : True,"msg": "OK"}), mimetype="application/json", status_code=200)

    


    
    
    
