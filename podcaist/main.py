import argparse

from podcaist.end_to_end import generate_entire_podcast


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf_path", type=str, required=True)
    parser.add_argument(
        "--model", type=str, required=True, default="gemini-2.0-flash-001"
    )
    parser.add_argument("--audio_model", type=str, required=True, default="kokoro")
    parser.add_argument("--remote", action="store_true")
    parser.add_argument("--save_locally", action="store_true", help="Save audio file locally")
    parser.add_argument("--local_output_path", type=str, default="./podcast_outputs", help="Local output directory for audio files")
    args = parser.parse_args()
    generate_entire_podcast(
        args.pdf_path, 
        args.model, 
        args.audio_model, 
        args.remote, 
        save_locally=args.save_locally,
        local_output_path=args.local_output_path
    )


if __name__ == "__main__":
    main()
