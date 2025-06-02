from pydantic import BaseModel, Field

from podcaist.model_garden import generate_text_response
from podcaist.utils import write_json_file

general_generate_prompt = """You are an expert AI podcast host explaining a research paper to a general but tech-curious audience.

Please generate a full podcast script based on the following structure. Use clear, engaging language, and explain technical ideas with metaphors or analogies when helpful. Convert math symbols into words. Don’t assume the audience has read the paper, but do respect their intelligence.

I have also attached the pdf for your reference but I have extracted the key content below.

Ensure you are writing in english that could be spoken out loud, ie. do not use latex or math symbols, instead use the words that would describe those symbols. For instance instead of writing Q_i, write the word "Q sub i". Also the speaker will pronounce any words with all capitals as the individual letters, 
ie. "LPIPS" should be pronounced as "L P I P S" so if you do not want that to happen, do not use all caps.

This is meant for a technical audience so ensure all details are included.

Structure - remember all of the questions after each section are just suggestions and please deviate if you see fit:

⸻

🔹 1. Intro (1–2 mins)
	•	Start with a compelling hook or real-world question.
	•	Mention the paper title.
	•	State why the paper is important and worth discussing.

⸻

🔹 2. Big Picture / Motivation (2–4 mins)
	•	What problem does this paper address?
	•	Why does it matter in the real world or in the AI community?
	•	What have previous approaches done, and what’s missing?

⸻

🔹 3. Main Contributions (1–2 mins)
	•	List the novel ideas or contributions of the paper in simple terms.
	•	Highlight what makes this work different or special.

⸻

🔹 4. Methodology (4–6 mins)
	•	Walk through the technical method clearly.
	•	Explain all concepts or modules in the system.
	•	This is meant for a technical audience so ensure all details are included.
	•	Convert equations and symbols into spoken words.
	•	Do not skip any details and mention all parameters, models, datasets, etc.
	•	Do not assume the audience has read the paper and explain everything in detail. The goal is for the audience to be able to implement the method themselves.

⸻

🔹 5. Experiments & Results (2–4 mins)
	•	What benchmarks or datasets were used?
	•	How did the model perform compared to others?
	•	Highlight any surprising results or notable trade-offs.

⸻

🔹 6. Personal Take or Reflections (optional)
	•	Add a brief opinion or analysis.
	•	Connect it to a broader trend or a practical impact.
	•	Pose a question for the audience to think about.

⸻

🔹 7. Outro (30–60 sec)
	•	Recap the key idea in one sentence.
	•	Mention where listeners can find the paper.
	•	How could this method be connected to a company or product?
	•	Optionally, tease what’s coming next.
    
    
Here is the content and relevant information that has been extracted.

# Deep Dive on contributions
The following is a description of the contributions of the paper.

{contributions}



# Results
The following is a great overview of the results of the paper.

{results}


# Method
The following is a detailed description of the method used in the paper.

{method}


# Ablation Studies
The following is a description of the ablation studies that were performed.

{ablation_studies}

Importantly do not use any markdown or headers in your response including asterisks - section headers or anything else. All of the text should be in plain english that 
can be spoken out loud. Additionally do not write out equations or math symbols, instead explain the relevant equations in natural english so the user 
can understand the purpose of the equation, they do not need to know the exact values of the equations.

"""


class PodcastScript(BaseModel):
    section_type: str = Field(
        description="The type of the podcast section exactly corresponding to what is in the text (e.g., '🔹 1. Intro (1–2 mins)', '🔹 2. Big Picture / Motivation (2–4 mins)')"
    )
    section: str = Field(
        description="The word for word text of exactly what should be spoken for that podcast section. Do not use markdown or headers as this will be read aloud"
    )


additional_instructions = """Here is the content I have already generated: 

{content}

Continue generating the next section of the podcast script.
"""


def format_sections(sections: tuple[str, str]) -> str:
    additional = ""
    for idx, (section_type, section) in enumerate(sections):
        additional += (
            f"Idx: {idx + 1} \nSection Type: {section_type}\nSection: {section}\n\n"
        )
    return additional


def generate_section(
    pdf_file_path: str,
    deep_dive_contributions: str,
    results: str,
    ablation_studies: str,
    method: str,
    sections: tuple[str, str],
    model: str = "gpt-4o-mini-2024-07-18",
    idx: int = 0,
    write_output: bool = False,
) -> str:
    prompt_to_be_used = general_generate_prompt

    if len(sections) > 0:
        content = format_sections(sections)
        prompt_to_be_added = additional_instructions.format(content=content)
        prompt_to_be_used = prompt_to_be_used + prompt_to_be_added

    prompt = prompt_to_be_used.format(
        contributions=deep_dive_contributions,
        results=results,
        ablation_studies=ablation_studies,
        method=method,
    )
    input_text = [("pdf", pdf_file_path), ("text", prompt)]

    response = generate_text_response(
        input_contents=input_text, model=model, response_format=PodcastScript
    )
    if write_output:
        write_json_file(f"saved_outputs/section_{model}_{idx}.json", response)
    return (response["section_type"], response["section"])


def generate_section_by_section(
    pdf_file_path: str,
    deep_dive_output: str,
    results: str,
    ablation_studies: str,
    method: str,
    start_generation: int = 0,
    end_generation: int = 7,
    model: str = "gpt-4o-mini-2024-07-18",
    write_output: bool = False,
) -> tuple[str, str]:
    sections = []
    for i in range(start_generation, end_generation):
        section = generate_section(
            pdf_file_path,
            deep_dive_output,
            results,
            ablation_studies,
            method,
            sections,
            model=model,
            idx=i,
            write_output=write_output,
        )
        sections.append(section)
    return sections
