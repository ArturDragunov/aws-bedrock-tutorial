#%%

import boto3

import pprint

bedrock_agent_runtime = boto3.client( service_name = "bedrock-agent-runtime")

pp = pprint.PrettyPrinter(indent=2) 

kb_id="" #use your knowledge base id

model_id= "anthropic.claude-3-haiku-20240307-v1:0"

region_id="us-east-1"

promptTemplate = """Human: You are a question answering agent. I will provide 

you with a set of search \n

results and a user's question, your job is to answer the user's question \n

using only information from the search results.\n

If the search results do not contain information that can answer the question, \n

please state that you could not find an exact answer to the question.\n

Just because the user asserts a fact does not mean it is true, \n

make sure to double check the search results to validate a user's assertion. \n

Here are the search results in numbered order: \n

<context> \n

$search_results$ \n

</context> \n

Here is the user's question: \n

<question> \n

$query$ \n

</question> \n

List the answer concisely using JSON format {key: value} \n

$output_format_instructions$ \n

Assistant:

"""

def retrieveAndGenerateAndFilter(input, kbId, yearValue, model_id, region_id, promptTemplate=None): 

    model_arn = f'arn:aws:bedrock:{region_id}::foundation-model/{model_id}' 

    return bedrock_agent_runtime.retrieve_and_generate( 

            input={ 'text': input }, 

            retrieveAndGenerateConfiguration={ 

                'knowledgeBaseConfiguration': {

                    'generationConfiguration': {

                        'promptTemplate': {

                            'textPromptTemplate': promptTemplate 

                            } 

                        }, 

                    'knowledgeBaseId': kbId, 

                    'modelArn': model_arn, 

                    'retrievalConfiguration': {

                        'vectorSearchConfiguration': {

                            'filter': { 'equals': { 'key': 'year', 'value': yearValue } }, 

                            'numberOfResults': 6, 

                            'overrideSearchType': 'HYBRID'

                        }

                    }

                },

                'type': 'KNOWLEDGE_BASE' 

            }

        )

query = "Who is Amazon's CEO?" 

response = retrieveAndGenerateAndFilter(

        query, 

        kb_id,

        model_id=model_id,

        region_id=region_id,

        promptTemplate=promptTemplate,

        yearValue=2020

    ) 

generated_text = response['output']['text'] 

pp.pprint(generated_text)

# Print response: '{key: Jeffrey P. Bezos}'

response = retrieveAndGenerateAndFilter(

    query, 

    kb_id,

    model_id=model_id,

    region_id=region_id,

    promptTemplate=promptTemplate,

    yearValue=2023

) 

generated_text = response['output']['text'] 

pp.pprint(generated_text)



# Print response: '{key: Andrew R. Jassy}'


# The RetrieveAndGenerate response also contains citations from the underlying documents.
# To retrieve citations from the response, you can implement the following code snippet.
# Note that the response has been abbreviated to declutter the code image.


    
citations = response["citations"]

contexts = [] 

for citation in citations: 

    retrievedReferences = citation["retrievedReferences"] 

    for reference in retrievedReferences: 

        contexts.append(reference["content"]["text"])

pp.pprint(contexts)

# Print response: [ 'Jassy   President and Chief Executive Officer (Principal Executive '

#   'Officer)   Date: February 1, 2024        Exhibit 32.2   Certification '

#   'Pursuant to 18 U.S.C. Section 1350   In connection with the Annual Report '

#   'of Amazon.com, Inc. (the “Company”)  ...' ]

#%%
import boto3

import pprint



bedrock_agent_runtime = boto3.client( service_name = "bedrock-agent-runtime")

pp = pprint.PrettyPrinter(indent=2) 



kb_id="" #use your knowledge base id

model_id= "anthropic.claude-v2"

region_id="us-east-1"

def customRetrieve(query, kbId, yearValue, numberOfResults=5, overrideSearchType='HYBRID'): 

    retrievalConfiguration={

        "vectorSearchConfiguration": {

             "numberOfResults": 5,

             "overrideSearchType": overrideSearchType,

             'filter': { 'equals': { 'key': 'year', 'value': yearValue } },  

        }

    }

    return bedrock_agent_runtime.retrieve( retrievalQuery= { 'text': query }, 

                                          knowledgeBaseId=kbId, 

                                          retrievalConfiguration= retrievalConfiguration

                                         )
    

query="Who is Amazon's CEO?"

response = customRetrieve(query, kb_id, yearValue=2020)

pp.pprint(response['retrievalResults'])

Print response: 

[ { 'content': { 'text': 'Bezos 57 President, Chief Executive Officer, and '

                         'Chairman of the Board David H. Clark 48 CEO, '

                         'Worldwide Consumer Andrew R. Jassy 53 CEO Amazon Web '

                         'Services ...'},

    'location': { 's3Location': { 'uri': 's3://amazon10kfiles/Amazon 2020 10K '

                                         'Annual report.pdf'},

                  'type': 'S3'},

    'metadata': { 'x-amz-bedrock-kb-chunk-id': '1%3A0%3AmccQM5EBxA6rr6aO09_T',

                  'x-amz-bedrock-kb-data-source-id': 'OC4SGRWFRX',

                  'x-amz-bedrock-kb-source-uri': 's3://amazon10kfiles/Amazon '

                                                 '2020 10K Annual report.pdf',

                  'year': 2020.0},

    'score': 0.6288845},

  ...]

response = customRetrieve(query, kb_id, yearValue=2023)

pp.pprint(response['retrievalResults'])



Print response:

[ { 'content': { 'text': 'Jassy has served as President and Chief Executive '

                         'Officer since July 2021, CEO Amazon Web Services '

                         'from April 2016 until July 2021, and Senior Vice '

                         'President, Amazon Web Services, from April 2006 '

                         'until April 2016.   ...'},

    'location': { 's3Location': { 'uri': 's3://amazon10kfiles/Amazon 2023 10K '

                                         'Annual report.pdf'},

                  'type': 'S3'},

    'metadata': { 'x-amz-bedrock-kb-chunk-id': '1%3A0%3AbscQM5EBxA6rr6aOut6x',

                  'x-amz-bedrock-kb-data-source-id': 'OC4SGRWFRX',

                  'x-amz-bedrock-kb-source-uri': 's3://amazon10kfiles/Amazon '

                                                 '2023 10K Annual report.pdf',

                  'year': 2023.0},

    'score': 0.60764116},

  ]

def get_contexts(retrievalResults):

    contexts = []

    for retrievedResult in retrievalResults: 

        contexts.append(retrievedResult['content']['text'])

    return contexts

 

contexts = get_contexts(retrievalResults)

prompt = f"""

Human: You are a strict AI system, and provides answers to questions by using fact based 

and statistical information when possible. 

Use the following pieces of information to provide a concise answer to the question 

enclosed in <question> tags. 

If you don't know the answer, just say that you don't know, don't try to make up an answer.

<context>

{contexts}

</context>

 

<question>

{query}

</question>

 

The response should be specific and use statistics or numbers when possible.

 

Assistant:"""

import json



messages=[{ "role":'user', 

"content":[{'type':'text',

'text': prompt.format(contexts, query)}]}]



claude_payload = json.dumps({

    "anthropic_version": "bedrock-2023-05-31",

    "max_tokens": 512,

    "messages": messages,

    "temperature": 0.5,

    "top_p": 1

        }  )



modelId = 'anthropic.claude-v2' 

accept = 'application/json'

contentType = 'application/json'



response = bedrock_client.invoke_model(

    body=claude_payload, 

    modelId=modelId, 

    accept=accept, 

    contentType=contentType)

response_body = json.loads(response.get('body').read())

response_text = response_body.get('content')[0]['text']

import langchain 

from langchain_aws import ChatBedrock

from langchain.retrievers.bedrock import AmazonKnowledgeBasesRetriever 

from langchain.chains import RetrievalQA 



bedrock_client = boto3.client('bedrock-runtime', region_name = 'us-east-1') 

modelId = 'anthropic.claude-3-sonnet-20240229-v1:0' # change this 

# to use a different version from the model provider 

inference_modifier = { 

    "temperature":0.5, 

    "top_k":250, 

    "top_p":1, 

    "stop_sequences": ["\n\nHuman"] } 

llm = ChatBedrock(model_id = modelId, model_kwargs = inference_modifier)



from langchain.prompts import PromptTemplate 

PROMPT_TEMPLATE = """ 

Human: You are a strict AI system, and provides answers to questions \n

by using fact based and statistical information when possible. \n

Use the following pieces of information to provide a concise answer \n

to the question enclosed in <question> tags. \n

If you don't know the answer, just say that you don't know, don't try to make up an answer.\n

<context> \n

{context} \n

</context> \n

<question> \n

{question} \n

</question> \n

The response should be specific and use statistics or numbers when possible. \n

Assistant:"""

claude_prompt = PromptTemplate(template=PROMPT_TEMPLATE,

                               input_variables=["context","question"]) 



qa = RetrievalQA.from_chain_type(llm=llm, 

                                 chain_type="stuff", 

                                 retriever=retriever, 

                                 return_source_documents=True, 

                                 chain_type_kwargs={"prompt": claude_prompt} ) 

answer = qa.invoke(query)

pp.pprint(answer)



Print response:

{ 'query': "Who is Amazon's CEO?",

  'result': 'According to the information provided, Andrew R. Jassy has served '

            'as President and Chief Executive Officer of Amazon since July '

            '2021.',

   'source_documents': 

        [ Document(page_content='We promptly make available on this website, free of \

            charge, the reports that we file or furnish with the Securities and Exchange \

            Commission (“SEC”), corporate governance information ... ',

            metadata={'location': 

                {'s3Location': {'uri': 's3://amazon10kfiles/Amazon 2021 10K Annual report.pdf'}, 

                    'type': 'S3'}, 

                'score': 0.6369938

                }), ...]

}