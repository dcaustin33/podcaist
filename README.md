# Podcaist

Podcaist is a tool that allows you to generate a podcast from a PDF file.

## Usage
Create and populate the `podcaist/api_secrets.py` file with your API keys. I could make
this a environment variable but who cares.
If you are not using elevenlabs or one of the model providers, you can just leave the
keys empty.
```
openai_api_key = ""
elevenlabs_api_key = ""
gemini_api_key = ""
```

Then run the following command to generate the podcast.
```
bash
python -m podcaist/main.py --pdf_path <path_to_pdf_file>
```
podcast will then be saved in the `podcast_outputs` directory.

