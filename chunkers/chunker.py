from transformers import pipeline
from typing import Any, List

class TableSplitter:
    def __init__(self, model_name: str = "google/flan-t5-base", **kwargs: Any) -> None:
        # Use a Hugging Face model for text generation (table extraction in this case)
        self.model = pipeline("text2text-generation", model=model_name)

        # Prompt template focused only on identifying tables with an example
        self.prompt_template = (
            "You are an expert in identifying tables in text and formatting them for LLM processing. "
            "Extract the tables from the following text and reformat them into a clean, structured format "
            "that retains all key details like symbols, numbers, and labels.\n\n"
            "Example:\n"
            "Text: \"The following table presents our total net revenues by segment. "
            "% Change (in millions) 2023 2022 Product Commerce $23,594 $19,955 18% 19%\"\n"
            "Reformatted Table:\n"
            "Segment: Product Commerce\n"
            "2023 Revenue: $23,594\n"
            "2022 Revenue: $19,955\n"
            "Change: 18%\n"
            "Change Constant Currency: 19%\n\n"
            "Now process the following text:\n\n{text}"
        )

    def split_text(self, text: str) -> List[str]:
        # Create the prompt asking for table extraction and formatting
        prompt = self.prompt_template.format(text=text)
        
        # Use the Hugging Face model to generate a response
        response = self.model(prompt, max_length=512, do_sample=False)[0]["generated_text"]
        
        # Return the extracted and reformatted table with all key information
        return response

class SummarizeSplitter:
    def __init__(self,max_length,  model_name: str = "facebook/bart-large-cnn", **kwargs: Any) -> None:
        # Use a Hugging Face model for summarization
        self.model = pipeline("summarization", model=model_name)
        self.max_length = max_length

        # You can adjust this prompt or approach based on your needs, but typically summarization doesn't need an explicit prompt.
        self.prompt_template = (
            "You are an expert at summarizing text into concise, clear representations. "
            "Summarize the following text:\n\n{text}"
        )

    def split_text(self, text: str) -> str:
        # Summarize the given text
        prompt = self.prompt_template.format(text=text)

        # Use the summarization model to generate a summary
        summary = self.model(prompt, max_length = self.max_length, min_length=30, do_sample=False)[0]['summary_text']
        
        # Return the summary
        return summary


class KeyConceptSplitter:
    def __init__(self, max_length, model_name: str = "google/flan-t5-base", **kwargs: Any) -> None:
        # Use a Hugging Face model for summarization and concept extraction
        self.model = pipeline("text2text-generation", model=model_name)
        self.max_length = max_length

        # Prompt template for identifying key concepts in the text
        self.prompt_template = (
            "You are an expert in financial documents and key concept extraction. "
            "Extract the most important sections and key concepts from the following 10-K report. "
            "Make sure to include sections like Risk Factors, Management’s Discussion, Financial Overview, and other relevant points.\n\n"
            "Text:\n\n{text}"
        )

    def split_text(self, text: str) -> List[str]:
        # Create the prompt asking for key concept extraction
        prompt = self.prompt_template.format(text=text)

        # Use the Hugging Face model to generate the key concept extraction
        key_concepts = self.model(prompt, max_length = self.max_length, do_sample=False)[0]["generated_text"]

        # Return the extracted key concepts
        return key_concepts