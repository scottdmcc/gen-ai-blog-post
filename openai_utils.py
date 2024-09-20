import base64
import re
from pathlib import Path

import openai
from openai.types import ImagesResponse
from openai.types.chat import ChatCompletion


def system_prompt() -> str:
    return """
    You are a helpful assistant to write blog posts.
    """.strip()


def user_prompt(subject: str) -> str:
    return f"""
    I would like to generate an interesting blog post that is about 2-3 paragraphs long. 
    The topic is {subject} and should include at least one unusual fact. 
    If you do not know anything about the topic, say you do not know instead of making up information. 
    The post should include a title that starts with 'Blog Title:' and no other markup.
    """.strip()


def dalle_prompt(subject: str) -> str:
    return f"""
    Pixel art showing '{subject}. Do not include any text in the image'.
    """.strip()


def create_blog_from_openai(config: dict, subject: str = 'Generative AI') -> tuple[str, str]:
    response: ChatCompletion = openai.chat.completions.create(
        model=config['OPENAI_MODEL'],
        messages=[
            {"role": "system", "content": system_prompt()},
            {"role": "user", "content": user_prompt(subject)},
        ],
        temperature=0.7,
        max_tokens=1500,
    )

    raw_content: str = response.choices[0].message.content
    title: str = re.search('Blog Title: (.*)\n\n', raw_content).group(1)
    content: str = raw_content.replace(f'Blog Title: {title}\n\n', '')

    return title, content



def create_image_from_openai(config: dict, subject: str, filename: str, save_path: Path) -> Path:
    res: ImagesResponse = openai.images.generate(
        model=config['OPENAI_DALLE_MODEL'],
        prompt=dalle_prompt(subject),
        size="1024x1024",
        quality="standard",
        n=1,
        response_format="b64_json"
    )
    image_data: str = res.data[0].b64_json

    return save_image(filename, image_data, save_path)


def save_image(filename: str, image_data, save_path: Path) -> Path:
    image_filepath: Path = Path(save_path / filename)
    decoded_img = base64.b64decode(image_data)

    with open(image_filepath, "wb") as f:
        f.write(decoded_img)

    return image_filepath
