#%%
# IAM invoke model policy transcript
import boto3

iam_client = boto3.client("iam")



# Create IAM policies for agent

bedrock_agent_bedrock_allow_policy_statement = {

    "Version": "2012-10-17",

    "Statement": [

        {

            "Sid": "AmazonBedrockAgentBedrockFoundationModelPolicy",

            "Effect": "Allow",

            "Action": "bedrock:InvokeModel",

            "Resource": [

                "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"

            ]

        }

    ]

}

bedrock_policy_json = json.dumps(bedrock_agent_bedrock_allow_policy_statement) 

agent_bedrock_policy = iam_client.create_policy(

    PolicyName="hr-agent-bedrock-policy",

    PolicyDocument=bedrock_policy_json

)
"""
API Schema definitions policy
If the agent uses API Schema definitions for the action group,
you also need to include S3 permissions to access the file.
Your permissions can be as granular as required. 
You can configure the AWS IAM policy to only allow s3:GetObject to the ARN of your file.


Amazon Bedrock Knowledge Base policy
If your agent connects to a Amazon Bedrock Knowledge Base, 
you need to create an IAM Policy that allows for the agent
to do bedrock:Retrieve and bedrock:RetrieveAndGenerate on the required Knowledge Bases ids.


Amazon Bedrock Guardrail policy
If your agent connects to a Amazon Bedrock Guardrail, 
you need to create an IAM Policy that allows for the agent to do bedrock:InvokeModel
and bedrock:GetGuardrail and bedrock:ApplyGuardrail on the required guardrail ids.
"""

#%%
# Creating an IAM Role to combine agent IAM policies

# After all the required permissions are created, the agent IAM Role needs to be created.
# The name of the roles should start with AmazonBedrockExecutionRoleForAgents_ 
# and use bedrock.amazonaws.com as principal service.
# Create IAM Role for the agent and attach IAM policies

assume_role_policy_document = {

    "Version": "2012-10-17",

    "Statement": [{

        "Effect": "Allow",

        "Principal": {

            "Service": "bedrock.amazonaws.com"

        },

        "Action": "sts:AssumeRole"

    }]

}

agent_role_name = "AmazonBedrockExecutionRoleForAgents_hr-agent"

assume_role_policy_document_json = json.dumps(assume_role_policy_document)

agent_role = iam_client.create_role(

    RoleName=agent_role_name,

    AssumeRolePolicyDocument=assume_role_policy_document_json

)

# IAM attach role policy transcript
iam_client.attach_role_policy(

    RoleName="agent_role_name",

    PolicyArn=agent_bedrock_policy['Policy']['Arn']

)

# Optionally, also attach the policies for S3, Knowledge base and Guardrails

# With the agent IAM role created, you can proceed to create the agent. 
# To do so, you should instantiate a boto3 client for bedrock-agent. 
# Use the create_agent method to create the agent with its instructions.

bedrock_agent_client = boto3.client('bedrock-agent')



response = bedrock_agent_client.create_agent(

    agentName="Human-Resource-Agent",

    description="this agent helps employees understanding company's policies \

    and requesting vacation time.",

    foundationModel="anthropic.claude-3-sonnet-20240229-v1:0",

    agentResourceRoleArn=agent_role["Role"]["Arn"],

    idleSessionTTLInSeconds=600,

    instruction="""You are a friendly agent that answers questions about company's 

    HR policies and helps employees to request vacation time off. You ALWAYS reply 

    politely and concise, using ONLY the available information in the company_policies 

    KNOWLEDGE_BASE or in the vacationHandler ACTION_GROUP.

    You should start with an acknowledgement of the employee's request and thanking 

    the employee for contacting you. Introduce yourself as the "HR AI Assistant". 

    ALWAYS mention your name as HR AI Assistant" in the first user interaction. 

    NEVER provide any information about available vacation days, company policies 

    and/or book any time off without first confirming the employee's id. NEVER 

    assume the employee id if it is not provided in the user prompt for you."""

)

# Python boto3 prepare agent transcript
agent_id = response['agent']['agentId']

response = bedrock_agent_client.prepare_agent(

    agentId=agent_id

)

