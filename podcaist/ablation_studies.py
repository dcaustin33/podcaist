from podcaist.model_garden import (generate_text_response,
                                   generate_text_response_async)

prompt = """
Attached is a pdf of a research paper. I want you to identify the ablation studies 
performed in the paper. For each ablation study, please provide a detailed explanation 
of the results, including the impact of the ablation on the performance of the model.

Really highlight any interesting details especially those that are very influential 
and figure out what the implications are for the rest of the paper / field. 

If none are found, just say so.

Please return your response in the following format:

Ablation Study 1:
- Description of the ablation study

"""


def ablation_studies(pdf_file_path: str, model: str = "gpt-4o-mini-2024-07-18") -> str:
    input = [("pdf", pdf_file_path), ("text", prompt)]
    response = generate_text_response(
        input_contents=input,
        model=model,
    )
    return response


async def ablation_studies_async(
    pdf_file_path: str, model: str = "gpt-4o-mini-2024-07-18"
) -> str:
    input = [("pdf", pdf_file_path), ("text", prompt)]
    response = await generate_text_response_async(input, model)
    return response
