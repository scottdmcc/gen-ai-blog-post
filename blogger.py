import time
from pathlib import Path

import openai
from dotenv import dotenv_values

from openai_utils import create_blog_from_openai, create_image_from_openai
from utils import check_folders, create_filename, create_image_name, file_configuration, generate_new_blog_html, \
    get_subject, push_to_repo, update_index_html


def main():
    config: dict = dotenv_values('.env')
    openai.api_key = config["OPENAI_API_KEY"]

    paths: dict[str, Path] = file_configuration(config)
    try:
        check_folders(paths)
    except FileNotFoundError as e:
        print(f'There is an error with the folders: {e}')
        exit(1)

    subject: str = get_subject()
    timestamp: int = int(time.time())

    blog_filename: str = create_filename(subject, timestamp)
    blog_image_name: str = create_image_name(subject, timestamp)
    title, content = create_blog_from_openai(config, subject)
    image_path: Path = create_image_from_openai(config, title, blog_image_name, paths["IMAGE_PATH"])

    generate_new_blog_html(paths['CONTENT_PATH'], blog_filename, blog_image_name, title, content)
    print(f'Article created: {title}')

    update_index_html(paths['REPO_PATH'], title, blog_filename)
    print(f'Index page updated: {title}')

    push_to_repo(paths, commit_message=f'Added blog post on {subject}')

if __name__ == '__main__':
    main()
