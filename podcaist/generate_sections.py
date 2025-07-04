import re
from typing import Optional
from pydantic import BaseModel, Field

from podcaist.model_garden import generate_text_response
from podcaist.utils import format_contributions

general_generate_prompt = """\
Here are the contributions that you have extracted from the attached paper:
{contributions}

Here is a deep dive on the method that you have written from the attached paper:
{method}

Here is a summary of the results that you have extracted from the attached paper:
{results}

Here is a summary of the limitations that you have extracted from the attached paper:
{limitations}

You are an expert podcast host of a podcast called The AI Research Deep Dive. \
The podcast is meant to have an engaging friendly conversational tone while being educational. \
You have been given a pdf of a research paper as well as a summary of the contributions, method, results and limitations. \
The task at hand is to synthesize the information into a coherent podcast. Specifically you are to write verbatim what is going \
to be read by a text to speech engine. That means everything should be in plain english without any math symbols or markdown that \
would not be readable by a text to speech engine. Avoid going deep into any math instead giving the user an overview of the math used \
in plain english that anybody could understand. The podcast is expected to be between 15-25 minutes. Write out numbers in like 64 \
to 'sixty four' and any acronyms should be spelled in all caps but avoid using if you can do so by expanding them.



I have also attached the research paper so reference it as you craft your responses. The contributions, method, results and limitations \
are also listed for reference, make sure everything said is grounded in your understanding of the attached pdf.

Here is a description of the sections that I want you to generate:

1. Introduction. 
The introduction should cover the "why" of the research paper. What makes this research paper important, what does it contribute to the community. \
Additionally, feel free to give a preview of the results or why it is important, but this is meant to entice the listener on why they should spend \
the next 15-25 minutes trying to understand the research paper.

2. Methods.
This part should cover exactly how the authors obtained their results. Your goal in this section is to give the listener a deep understanding \
of exactly what the authors did. The listener wants to understand exactly what they did, assuming the audience is a person with a Master's in AI. \
At the end of your explanation the listnee should have the necessary knowledge to sketch the pseudocode and \
explain the method to others. Feel free to explore whether the method relies on a theoretical understanding or \
empirical studies. Your task is to focus on this contribution in particular. The listener should be able to have a conversation \
with another person at the end on how the authors obtained their results and what were some key steps they took in order to do so. \
A key aspect to focus on is what makes this method different from other approaches and why is it advantageous. This should be the main focus of the podcast.

3. Results and limitations.
The goal of this section is give the listener an understanding of how the authors chose to quantitively or qualitatively evaluate their method. \
Bring up whatever is necessary to give the reader an understanding of the datasets and metrics used. Weaving into the conversation should be \
your judgement on whether these were standard evaluation procedures or if they left something out that could have been used. Additonally, \
discuss if the results back up the authors claims throughout the paper. Also discuss any limitations to the approach the authors used in the results \
or even the method that you see as important to understanding the impact this paper will have.

4. Conclusion.
This section should serve as a wrap up for the podcast as a whole. Fill in any final holes or questions that the listener may have. \
Additionally discuss the impact and implications the paper has on the research and or business community and what future work may look like to further improve the method. \
Do not tease any future episodes just keep this podcast about the current paper at hand.


Generate the section after thinking through your approach and what would be best to listen to as a podcast listener. After detailing your thoughts in the response start the \
actual word for word generation that will be read by the text to speech engine with the string 'STARTING THE GENERATION NOW'. I will use that to split the response \
automatically so it is extremely important you do that. Do not include any other text like 'Introduction' or anything else that resemble section titles. The response will be fed DIRECTLY \
into a text to speech engine so every word will be read out loud after seeing the string 'STARTING THE GENERATION NOW'. Do NOT include anything about intro music or anything else \
of the sort that is not considered part of the podcast content. Do NOT use asterisks '*' or any other markdown formatting.
"""

custom_instructions_prompt = """\
Here are some additional instructions from the user in regards to this paper that you should especially focus on:
{custom_instructions}
"""

def remove_music_lines(text: str) -> str:
    """Remove any lines that contain the word 'music' inside parentheses."""
    lines = text.split('\n')
    filtered_lines = []
    
    for line in lines:
        # Check if the line contains 'music' inside parentheses
        if not re.search(r'\([^)]*music[^)]*\)', line, re.IGNORECASE):
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def generate_podcast(
    pdf_file_path: str,
    contributions: list[str],
    method: str,
    results: str,
    limitations: str,
    model: str = "gemini-2.5-pro",
    custom_instructions: str | None = None,
    api_key: str | None = None,
) -> str:
    formatted_contributions = format_contributions(contributions)
    input_to_the_model = general_generate_prompt.format(
        contributions=formatted_contributions,
        method=method,
        results=results,
        limitations=limitations,
    )
    if custom_instructions:
        input_to_the_model = custom_instructions_prompt.format(custom_instructions=custom_instructions) + "\n\n" + input_to_the_model
    input = [
        ("pdf", pdf_file_path),
        ("text", input_to_the_model),
    ]
    response = generate_text_response(input, model, api_key=api_key)
    response = response.replace("STARTING THE GENERATION NOW", "")
    response = remove_music_lines(response)
    return response