import argparse
from pathlib import Path

from bs4 import BeautifulSoup as bs4, BeautifulSoup, ResultSet, Tag
from git import Repo
from jinja2 import Environment, FileSystemLoader
from slugify import slugify


def file_configuration(config: dict) -> dict:
    local_repo: Path = Path(config["PATH_TO_LOCAL_REPO"])

    return {
        "REPO_PATH": local_repo,
        "GIT_PATH": Path(local_repo / '.git'),
        "CONTENT_PATH": Path(local_repo / 'content'),
        "IMAGE_PATH": Path(local_repo / 'content' / 'images'),
    }


def check_folders(paths: dict) -> None:
    if not paths["CONTENT_PATH"].exists():
        raise FileNotFoundError(f'Cannot find {paths["CONTENT_PATH"].as_posix()}')
    if not paths["IMAGE_PATH"].exists():
        paths["IMAGE_PATH"].mkdir(parents=True, exist_ok=True)


def get_subject() -> str:
    parser = argparse.ArgumentParser(prog='blogger',
                                     description='CLI Blogger via Generative AI',
                                     epilog='Scott McCollough')
    parser.add_argument('subject', nargs='?')
    args = parser.parse_args()
    if args.subject is None:
        return 'Generative AI'

    return args.subject


def create_filename(subject: str, timestamp: int) -> str:
    return f'{slugify(subject)}-{timestamp}.html'


def create_image_name(subject: str, timestamp: int) -> str:
    return f'{slugify(subject)}-{timestamp}.png'


def generate_new_blog_html(content_path: Path, filename: str, blog_image_name: str, title: str, content: str):
    blog_template: str = 'blog.html'
    environment: Environment = Environment(loader=FileSystemLoader('templates/'))
    template = environment.get_template(blog_template)
    page: str = template.render(
        blog_image_name=blog_image_name,
        title=title,
        content=content.replace('\n', '<br>\n'))

    with open(Path(content_path / filename), 'w', encoding='utf-8') as f:
        f.write(page)


def update_index_html(repo_path: Path, title: str, filename: str):
    with open(repo_path / "index.html") as index:
        index_page: BeautifulSoup = bs4(index.read(), features="html.parser")

    article_list: ResultSet = index_page.select("ul.articles li")
    last_link: Tag = article_list[-1]

    new_option: Tag = index_page.new_tag('li')
    link_to_new_article: Tag = index_page.new_tag("a", href=Path(Path('content') / filename))
    link_to_new_article.string = title

    new_option.append(link_to_new_article)
    last_link.insert_after(new_option)

    with open(repo_path / "index.html", "w") as f:
        f.write(str(index_page.prettify(formatter='html')))


def push_to_repo(paths: dict, commit_message="Added new blog post"):
    repo = Repo(paths['GIT_PATH'])
    repo.git.add(all=True)
    repo.index.commit(commit_message)

    origin = repo.remote(name='origin')
    origin.push()
