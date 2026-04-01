import argparse
import re
from pathlib import Path

EXERCISE_HEADER_RE = re.compile(
    r'(?im)^[ \t#>*-]*<h3[^>]*>\s*Exercise\s+(\d+)\b.*?</h3>\s*$',
    re.MULTILINE,
)


def parse_exercise_list(raw):
    exercises = set()
    for part in raw.split(","):
        token = part.strip()
        if not token:
            continue
        if not token.isdigit():
            raise ValueError(f"Invalid exercise value: {token}")
        number = int(token)
        if number <= 0:
            raise ValueError(f"Exercise number must be > 0: {number}")
        exercises.add(number)

    if not exercises:
        raise ValueError("At least one exercise must be provided.")

    return exercises


def filter_exercises_from_text(content, keep_exercises):
    matches = list(EXERCISE_HEADER_RE.finditer(content))
    if not matches:
        return content, []

    kept_sections = []
    found = []

    for idx, match in enumerate(matches):
        exercise_number = int(match.group(1))
        found.append(exercise_number)

        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)

        if exercise_number in keep_exercises:
            kept_sections.append(content[start:end].strip("\n"))

    filtered = "\n\n".join(section for section in kept_sections if section)
    if filtered:
        filtered += "\n"

    return filtered, found


def preprocess_directory(target_dir, extension, keep_exercises):
    ext = extension.lstrip(".").lower()
    files = list(Path(target_dir).rglob(f"*.{ext}"))

    processed = 0
    changed = 0
    without_headers = 0

    for path in files:
        original = path.read_text(encoding="utf-8")
        filtered, found = filter_exercises_from_text(original, keep_exercises)

        processed += 1
        if not found:
            without_headers += 1
            continue

        if filtered != original:
            path.write_text(filtered, encoding="utf-8")
            changed += 1

    return {
        "processed": processed,
        "changed": changed,
        "without_headers": without_headers,
        "extension": ext,
    }


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Keep only selected exercise blocks in converted files."
    )
    parser.add_argument(
        "--target-dir",
        required=True,
        help="Directory containing converted files to preprocess.",
    )
    parser.add_argument(
        "--extension",
        choices=["py", "md"],
        required=True,
        help="File extension to preprocess.",
    )
    parser.add_argument(
        "--keep-exercises",
        required=True,
        help="Comma-separated exercise numbers to keep (example: 1,4).",
    )
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    keep_exercises = parse_exercise_list(args.keep_exercises)
    result = preprocess_directory(args.target_dir, args.extension, keep_exercises)

    print(
        f"Preprocessing complete for .{result['extension']} files in {args.target_dir}: "
        f"processed={result['processed']}, changed={result['changed']}, "
        f"without_headers={result['without_headers']}"
    )


if __name__ == "__main__":
    main()
