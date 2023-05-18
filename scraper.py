from bs4 import BeautifulSoup
import click
import html
import requests

"""
Given a list of artist and label URLs, pull blurbs for all available albums
"""
# TODO: SET UP BLACK
# TODO: Make more general to do more with the API
# TODO: Make a separate package for parsing bandcamp stuff


def get_albums(entity_url: str) -> list:
    """
    Given an entity, get list of albums
    """
    entity_url = entity_url.rstrip("/")
    response = requests.get(entity_url)
    soup = BeautifulSoup(response.text, "html.parser")
    albums = []
    for link in soup.find_all('a'):
        url = link.get('href')
        if url is not None and "/album/" in url:
            if url.startswith("http"):
                albums.append(url)
            else:
                albums.append(f"{entity_url}{url}")
    return albums


def get_blurb(album_url: str) -> str:
    """
    Given an album, get blurb if it exists and clean it up
    :param album_url:
    :return:
    """
    response = requests.get(album_url)
    soup = BeautifulSoup(response.text, "html.parser")
    meta = soup.find("meta", content=True)
    blurb = html.unescape(meta.get("content"))
    return blurb


def main():
    album_list = []
    blurb_list = []

    # Read list of entities
    with open("labels") as f:
        entity_list = [x.rstrip("\n") for x in f.readlines()]

    # For each entity, get album list
    click.echo(f"Number of entities to process: {len(entity_list)}")
    with click.progressbar(entity_list) as entities:
        for entity in entities:
            album_list.extend(get_albums(entity_url=entity))

    # Use total album list to pull blurbs
    click.echo(f"Number of albums to process: {len(album_list)}")
    with click.progressbar(album_list) as albums:
        for album in albums:
            try:
                blurb_list.append(get_blurb(album_url=album))
            except requests.exceptions.ConnectionError:
                click.prompt(f"Unable to connect for album url {album}, skipping.\n")
                continue

    click.echo("Writing blurbs to textfile")
    with open("blurbs.txt", "w+") as f:
        for blurb in blurb_list:
            f.write(f"{blurb}\n====================\n")


if __name__ == "__main__":
    main()
