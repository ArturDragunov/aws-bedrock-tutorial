#%%
import boto3
from langchain_aws import BedrockLLM
bedrock_client = boto3.client('bedrock-runtime',region_name="us-east-1")
inference_modifiers = {"temperature": 0.3, "maxTokenCount": 512}
llm = BedrockLLM(
    client = bedrock_client,
    model_id="amazon.titan-tg1-large",
    model_kwargs =inference_modifiers
    streaming=True,
)
response = llm.invoke("What is the largest city in Vermont?")
print(response)

#%%
"""Chat models example

The following example demonstrates how you can get a response
from an LLM by passing a user request to the LLM."""
from langchain_aws import ChatBedrock as Bedrock
from langchain.schema import HumanMessage
chat = Bedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0",
               model_kwargs={"temperature":0.1})

messages = [
     HumanMessage(
          content="I would like to try Indian food, what do you suggest should I try?"
     )
]
chat.invoke(messages)

#%%
from langchain_community.embeddings import BedrockEmbeddings

embeddings = BedrockEmbeddings(
    region_name="us-east-1",
    model_id="amazon.titan-embed-text-v1"
)

embeddings.embed_query("Cooper is a puppy that likes to eat beef")

#%%
"""When building generative AI applications using the RAG approach,
documents must be loaded from different sources to the LLMs to generate embeddings.

LangChain provides the document loaders component, which is responsible for loading documents from various sources.
Sources can include a database, an online store, or a local store.
You can index and use information from these sources for information retrieval.
You can use the document loaders to load different types of documents, such as HTML, PDF, and code. For more information,
refer to Document Loaders(opens in a new tab)."""
from langchain.document_loaders import S3FileLoader

loader = S3FileLoader("mysource_bucket","sample-file.docx")
data = loader.load()

#%%
"""
Retriever example 

The following example demonstrates the use of the AmazonKendraRetriever to query an Amazon Kendra
index and pass the results from that call to an LLM as context along with a prompt.
"""
from langchain_aws.retrievers import AmazonKendraRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_aws import ChatBedrock 


llm = ChatBedrock(
    model_kwargs={"max_tokens_to_sample":300,"temperature":1,"top_k":250,"top_p":0.999,"anthropic_version":"bedrock-2023-05-31"},
    model_id="anthropic.claude-3-sonnet-20240229-v1:0"
)

retriever = AmazonKendraRetriever(index_id=kendra_index_id,top_k=5,region_name=region)

prompt_template = """ Human: This is a friendly conversation between a human and an AI.
The AI is talkative and provides specific details from its context but limits it to 240 tokens.
If the AI does not know the answer to a question, it truthfully says it
does not know.

Assistant: OK, got it, I'll be a talkative truthful AI assistant.

Human: Here are a few documents in <documents> tags:
<documents>
{context}
</documents>
Based on the above documents, provide a detailed answer for, {question}
Answer "do not know" if not present in the document.

Assistant:
 """

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

response = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt":PROMPT},
    verbose=True)

#%%
# with OpenSearch you manually chunk, embed, and store documents, 
# then embed queries and do similarity search. With Kendra, 
# you skip all that because Kendra does exactly the same work once at indexing time,
# just fully managed and hidden from you. At query time, Kendra only embeds the query and searches its precomputed
# index—it does not reprocess documents. The tradeoff is convenience and enterprise features versus cost and control.
import os
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch

index_name = os.environ["AOSS_INDEX_NAME"]
endpoint = os.environ["AOSS_COLLECTION_ENDPOINT"]

embeddings = BedrockEmbeddings(client=bedrock_client)

vector_store = OpenSearchVectorSearch(
    index_name=index_name,
    embedding_function=embeddings,
    opensearch_url=endpoint,
    use_ssl=True,
    verify_certs=True,
)
retriever = vector_store.as_retriever()

#%%
# ConversationBufferMemory: The ConversationBufferMemory is the most common type of memory in LangChain.
# It includes past conversations that happened between the user and the LLM.
# ConversationChain: The ConversationBufferMemory is built on top of ConversationChain, which is designed for managing conversations.
from langchain.chains import ConversationChain
from langchain_aws import BedrockLLM
from langchain.memory import ConversationBufferMemory
bedrock_client = boto3.client('bedrock-runtime',region_name="us-east-1")


titan_llm = BedrockLLM(model_id="amazon.titan-tg1-large", client=bedrock_client)
memory = ConversationBufferMemory()

conversation = ConversationChain(
    llm=titan_llm, verbose=True, memory=memory
)

print(conversation.predict(input="Hi! I am in Los Angeles. What are some of the popular sightseeing places?"))
# Ask a question without mentioning the city Los Angeles to find out how the model responds according to the previous conversation.
print(conversation.predict(input="What is closest beach that I can go to?"))