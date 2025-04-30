from podcaist.model_garden import (generate_text_response,
                                   generate_text_response_async)

prompt = """Attached is a pdf of a research paper. I want you to summarize the results of the paper. 
Specifically focus on the results section of the paper and who they are compared to. Please make sure to 
explain how the results were obtained and why they are significant. 

If they outperform other methods also highlight that. If they underperform other methods also highlight that.

Explain in detail the metrics they use, and the datasets they evaluate on. Give specific numbers and details if it would help 
someone to understand the results better.

Please return your response in the following format:

Results:
- Summary of the results
- Comparison to other methods
- Key results
"""


def results(pdf_file_path: str, model: str = "gpt-4o-mini-2024-07-18") -> str:
    input = [("pdf", pdf_file_path), ("text", prompt)]
    response = generate_text_response(
        input_contents=input,
        model=model,
    )
    return response


async def results_async(
    pdf_file_path: str, model: str = "gpt-4o-mini-2024-07-18"
) -> str:
    input = [("pdf", pdf_file_path), ("text", prompt)]
    response = await generate_text_response_async(input, model)
    return response
