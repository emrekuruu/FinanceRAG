from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Any, Dict
import json

class TableExtractor:
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo") -> None:
        # Initialize OpenAI chat model in LangChain
        self.llm = ChatOpenAI(model_name=model_name, openai_api_key=api_key)
        
        # Define a specific prompt with an example output for clarity
        self.prompt_template = ChatPromptTemplate.from_template(
            """
            Please convert the following hierarchical table data into structured JSON format. 
            There may be more than one table in the text. 
            Ignore any information that does not represent a column, row, or hierarchy. 
            If there is any currency mentioned (like millions or thousands), do not include it in the table but add it as context in the final JSON object.
            Ignore any information that does not represent a column, row, or hierarchy.

            **Input Table Data:** 
            {text}

            **Example Output:**
            The output should be structured as follows:
            - A key named tables containing a list of table objects.
            - Each table object should include:
            - table_id which identifies the table 
            - context as a dictionary providing information about the currency used (e.g., context: "millions.").
            - description as a short text description of the table (e.g., "A short description of the table.").

            Please structure the output accordingly.
            """
        )
        
        # Create a RunnableSequence using the pipe operator
        self.runnable = self.prompt_template | self.llm
        
    def extract_table(self, text: str) -> Dict[str, Any]:
        response = self.runnable.invoke({"text": text})  # Use invoke to get the response
        # Extract the text content from the response object
        json_string = response.content if hasattr(response, 'content') else str(response)
        table_data = json.loads(json_string)  # Now load the JSON from the string
        return table_data
