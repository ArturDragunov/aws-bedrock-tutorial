#%%
"""ListFoundationModels
This method is used to provide a list of Amazon Bedrock foundation models that you can use.
The following example demonstrates how to list the base models using Python."""
import boto3
import json
bedrock = boto3.client(service_name='bedrock')
model_list=bedrock.list_foundation_models()
for x in range(len(model_list.get('modelSummaries'))):
     print(model_list.get('modelSummaries')[x]['modelId'])

#%%
"""InvokeModel

This API invokes the specified Amazon Bedrock model to run inference using the input provided in the request body.
You use InvokeModel to run inference for text models, image models, and embedding models."""
bedrock_rt = boto3.client(service_name='bedrock-runtime')
prompt = "What is Amazon Bedrock?"
configs= {
"inputText": prompt,
"textGenerationConfig": {
"maxTokenCount": 4096,
"stopSequences": [],
"temperature":0,
"topP":1
}
}
body=json.dumps(configs)
modelId = 'amazon.titan-tg1-large'
accept = 'application/json'
contentType = 'application/json'
response = bedrock_rt.invoke_model(
     body=body,
     modelId=modelId,
     accept=accept,
     contentType=contentType
)
response_body = json.loads(response.get('body').read())
print(response_body.get('results')[0].get('outputText'))

#%%
"""Converse API Example
This API provides a consistent interface that works with all models that support messages. 
This allows you to write code once and use it with different models.
If a model has unique inference parameters, you can also pass those unique parameters to the model."""
import boto3
client = boto3.client("bedrock-runtime")
model_id = "amazon.titan-tg1-large"

# Inference parameters to use.
temperature = 0.5
top_p = 0.9

inference_config={"temperature": temperature,"topP": top_p}

# Setup the system prompts and messages to send to the model.
system_prompts = [{"text": "You are a helpful assistance. Please answer the query politely."}]
conversation = [
    {
        "role": "user",
        "content": [{"text": "Hello, what is the capital of France?"}]
    }
]
# Use converse API
response = client.converse(
    modelId=model_id,
    messages=conversation,
    inferenceConfig=inference_config
)
print(response['output']['message']["content"][0]["text"])
