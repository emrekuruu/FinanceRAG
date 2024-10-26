from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from typing import Any, Dict
import json
import pandas as pd 

class TableExtractor:
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo") -> None:
        # Initialize OpenAI chat model in LangChain
        self.llm = ChatOpenAI(model_name=model_name, openai_api_key=api_key)
        
        # Define a specific prompt with a clear example for expected output
        self.prompt_template = ChatPromptTemplate.from_template(
            """You will take the following text as input and extract a single table from it, preserving only rows and columns as shown in the table. There will be paragraph text before the table; ignore it and extract the table only.

            Text:
            {text}

            You should extract the table and return it in the following JSON format:
            **EXAMPLE OUTPUT**
            {{
                "table": [
                    [
                        "column1",
                        "column2",
                        "column3",
                        "column4"
                    ],
                    [
                        "row1",
                        "value1",
                        "value2",
                        "value3"
                    ],
                    [
                        "row2",
                        "value4",
                        "value5",
                        "value6"
                    ]
                ]
            }}
            """
        )
        
        # Set up the LangChain LLMChain for querying OpenAI
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        
    def extract_table(self, text: str) -> pd.DataFrame:
        response = self.chain.run({"text": text})
        table_data = json.loads(response)                
        return table_data
