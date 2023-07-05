import json
import requests
from datetime import datetime
from pathlib import Path


# Format timestamp to YYMMDD
def format_timestamp(timestamp):
    ts = str(timestamp)[:-3]
    date_time = datetime.fromtimestamp(int(ts))
    date = date_time.strftime("%y%m%d")
    return date


# Remove invalid characters from the post title
def clean_title(title):
    while title.endswith(' '):
        title = title.rstrip()
    while title.endswith('.'):
        title = title.rstrip('.')
    invalid = r'<>:"/\|?*'
    return ''.join([c for c in title if c not in invalid])


# Check post type and add to appropriate list
def get_posts(data):
    posts = []
    for content in data:
        if content["contentType"] == "POST":
            posts.append(content)
    return posts


def get_videos(data):
    videos = []
    for content in data:
        if content["contentType"] == "VIDEO":
            if "originPost" in content:
                videos.append(content)
            elif len(content["officialVideo"]["badges"]) > 0:
                videos.append(content)
            elif "SHOWCASE" in content["title"].upper():
                videos.append(content)
    return videos


# Create directory for each post
def download_posts(post_list):
    for imagePost in post_list:
        if imagePost["attachments"]["photoCount"] > 0:
            d = format_timestamp(imagePost["createdAt"])
            title = clean_title(imagePost["title"])
            folder_path = Path(imagePost["author"]["nickname"]) / Path(f'{d} {title} [{imagePost["postId"]}]')
            if not folder_path.exists():
                folder_path.mkdir(parents=True)
            # Download images from post
            for photo_id in imagePost["attachments"]["photo"]:
                image_url = imagePost["attachments"]["photo"][photo_id]["url"]
                res = requests.get(image_url)
                try:
                    res.raise_for_status()
                    img_path = folder_path / f"{photo_id}.jpg"
                    if not img_path.exists():
                        print(f"Downloading {folder_path.stem}\\{photo_id}.jpg...")
                        with open(folder_path / f"{photo_id}.jpg", 'wb') as image:
                            for chunk in res.iter_content():
                                image.write(chunk)
                    else:
                        print(f"{folder_path.stem}\\{photo_id}.jpg already exists, skipping download...")
                except Exception as e:
                    print(f"There was a problem: {e}")
            # Write post body to text file
            if "plainBody" in imagePost:
                with open(folder_path / "body.txt", 'w', encoding="utf8") as body:
                    print("Writing post body...")
                    body.write(imagePost["plainBody"])
                    if imagePost["attachments"]["videoCount"] > 0:
                        body.write(f'\n{imagePost["url"]}')


# Get list of videos with multinational titles
def write_multi_titles(video_list):
    title_list = []
    for video in video_list:
        if len(video["officialVideo"]["multinationalTitles"]) > 1:
            video_data = {"Date": f'{format_timestamp(video["createdAt"])}'}
            for title in video["officialVideo"]["multinationalTitles"]:
                if title["locale"] == "en_US":
                    video_data["English Title"] = title["label"]
                elif title["locale"] == "ko_KR":
                    video_data["Korean Title"] = title["label"]
            title_list.append(video_data)
    print("Writing multinational titles to file...")
    with open("multi_titles.json", 'w', encoding="utf8") as out_file:
        json.dump(title_list, out_file, ensure_ascii=False, indent=4)


def vidlist_to_file(vidlist):
    with open('vidlist.txt', 'w') as f:
        print("Writing video URLs to file...")
        for video in vidlist:
            f.write(video["url"] + '\n')


def main():
    # Load JSON data from file(s).
    # posts = []
    videos = []
    for n in range(1, 33):
        filepath = Path(r"path\to\group", f'group{n}.json')
        vlive_json = json.loads(filepath.read_text(encoding="utf-8"))
        # posts = posts + get_posts(vlive_json["data"])
        videos = videos + get_videos(vlive_json["data"])
    # print(len(posts))
    # download_posts(posts)
    # write_multi_titles(videos)
    vidlist_to_file(videos)


if __name__ == "__main__":
    main()
