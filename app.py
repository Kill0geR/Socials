from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from pytubefix import YouTube
from moviepy.editor import *
import os
import time
import uuid
import zipfile
import instaloader
import requests
import shutil
import pyktok as pyk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import subprocess
import yt_dlp
import requests
from io import BytesIO
from bs4 import BeautifulSoup
import praw
import re


def youtube_to_mp3(url):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        video_file = video.download(output_path="downloads", filename='temp_video')

        get_song_name = f'downloads/Audios/{uuid.uuid4()}.mp3'
        video_clip = AudioFileClip(video_file)
        video_clip.write_audiofile(get_song_name)

        os.remove(video_file)
        return get_song_name
    except Exception as e:
        print(e)
        return False

    print("Conversion completed successfully!")


def get_twitter_profile_picture(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(1.5)

    try:
        links = driver.find_elements(By.TAG_NAME, "a")

        photo_link = None
        for link in links:
            href = link.get_attribute("href")
            if href and href.endswith("/photo"):
                photo_link = link
                break

        if not photo_link:
            print("Kein Link mit /photo gefunden.")
            return

        img = photo_link.find_element(By.TAG_NAME, "img")
        img_url = img.get_attribute("src")
        print(f"Bild-URL gefunden: {img_url}")

        response = requests.get(img_url)
        filename = f"downloads/Profiles/{uuid.uuid4()}.jpg"
        with open(filename, "wb") as f:
            f.write(response.content)

        return filename

    except Exception as e:
        print(f"Fehler: {e}")
    finally:
        driver.quit()


def download_twitter_videos(url):
    got_video = False
    got_image = False

    video_file = f'downloads/Videos/{uuid.uuid4()}.mp4'

    try:
        try:
            ydl_opts = {
                'format': 'bv*+ba/best',
                'merge_output_format': 'mp4',
                'outtmpl': video_file,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                got_video = True

        except yt_dlp.utils.DownloadError as e:
            print(e)

        finally:
            # Headless Chrome konfigurieren
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            # Starte den Browser
            # driver = webdriver.Chrome(options=options, service=ChromeDriverManager().install())
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(1.5)

            images = driver.find_elements("tag name", "img")
            media_urls = [img.get_attribute("src") for img in images if "pbs.twimg.com/media" in img.get_attribute("src")]

            driver.quit()

            print(media_urls)
            zip_buffer = BytesIO()
            # Bild speichern
            if media_urls:
                got_image = True
                if len(media_urls) == 1 and not got_video:
                    filename = f"downloads/Images/{uuid.uuid4()}.jpg"
                    with open(filename, "wb") as f:
                        content = requests.get(media_urls[0]).content
                        f.write(content)

                    return filename

                else:
                    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                        for idx, url in enumerate(media_urls):
                            img_data = requests.get(url).content
                            zip_file.writestr(f"bild_{idx + 1}.jpg", img_data)
                            print(f"Bild {idx + 1} hinzugefügt: {url}")

            if got_video and not got_image:
                return video_file

            elif got_image and got_video:
                with open(video_file, "rb") as f:
                    data = f.read()

                with zipfile.ZipFile(zip_buffer, "a") as zip_file:
                    zip_file.writestr(video_file.split("/")[-1], data)

                os.remove(video_file)

            if True in [got_video, got_image]:
                zip_filename = f"downloads/Images/{uuid.uuid4()}.zip"
                with open(zip_filename, "wb") as f:
                    f.write(zip_buffer.getvalue())

                return zip_filename

            return False

    except Exception as e:
        print(f"Fehler: {e}")
        return False


def download_reddit_videos(url):
    filename = f'downloads/Videos/{uuid.uuid4()}.mp4'
    ydl_opts = {
        'format': 'bv*+ba/best',
        'merge_output_format': 'mp4',
        'outtmpl': filename,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filename


def download_insta_images(post_url):
    try:
        return_filename = ""
        loader = instaloader.Instaloader()

        target_file = uuid.uuid4()
        real_folder = f"downloads/Images/{target_file}"
        os.mkdir(real_folder)

        shortcode = post_url.split("/p/")[-1].split("/")[0]
        print(shortcode)

        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        loader.download_post(post, target=target_file)

        valid_files = []
        for each_file in os.listdir(str(target_file)):
            if each_file.split(".")[-1] in ["jpg", "jpeg", "png", "mp4"]:
                valid_files.append(f"{target_file}/{each_file}")

            else:
                os.remove(f"{target_file}/{each_file}")

        if len(valid_files) > 1:
            zipname = f"{real_folder}/{uuid.uuid4()}.zip"

            with zipfile.ZipFile(zipname, 'w') as zipf:
                for file in valid_files:
                    zipf.write(file, arcname=file.split('/')[-1])
                    os.remove(file)

            return_filename = zipname

        else:
            new_filename = f"downloads/Images/{uuid.uuid4()}.jpeg"
            with open(new_filename, "wb") as f:
                with open(valid_files[0], "rb") as file:
                    content = file.read()

                f.write(content)
                os.remove(valid_files[0])
                return_filename = new_filename

        os.rmdir(str(target_file))

        return return_filename

    except Exception as e:
        print(e)
        return False


def download_instagram_profile_picture(url):

    username = url.split('www.instagram.com')[-1].split("/")[1]

    L = instaloader.Instaloader()

    profile = instaloader.Profile.from_username(L.context, username)

    profile_picture_url = profile.profile_pic_url
    response = requests.get(profile_picture_url)
    filename = f"downloads/Profiles/{uuid.uuid4()}.jpg"
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        return filename
    else:
        return False


def insta_download_reel(reel_url):
    try:
        L = instaloader.Instaloader()

        target_folder = uuid.uuid4()
        real_folder = f"downloads/Reels/{target_folder}"

        post = instaloader.Post.from_shortcode(L.context, reel_url.split("reel")[-1].split("/")[1])

        L.download_post(post, target=target_folder)

        filenames = f'{post.date.strftime("%Y-%m-%d_%H-%M-%S")}_UTC'

        os.mkdir(real_folder)
        mp4_file = ""
        for each_file in os.listdir(str(target_folder)):
            if each_file.endswith(".mp4"):
                mp4_file = each_file
                shutil.move(f"{target_folder}/{each_file}", f"{real_folder}")
            else:
                os.remove(f"{target_folder}/{each_file}")

        os.rmdir(str(target_folder))

        return f"{real_folder}/{mp4_file}"
    except Exception as e:
        print(e)
        return False


def download_tiktok(url):
    try:
        change_dir = f"downloads/TikTok_Video/{uuid.uuid4()}"
        os.mkdir(change_dir)
        os.chdir(change_dir)

        # pyk.specify_browser('chrome')

        pyk.save_tiktok(url, True)
        filename = f"{change_dir}/{os.listdir()[0]}"
        os.chdir("../../..")
        return filename

    except Exception as e:
        print(e)
        os.chdir("../..")


def download_tiktok_profile_picture(link):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    driver.get(link)
    time.sleep(1.5)

    try:
        img_element = driver.find_element(By.CSS_SELECTOR, "img[class*='ImgAvatar']")
        img_url = img_element.get_attribute("src")
        driver.quit()
        filename = f"downloads/Images/{uuid.uuid4()}.jpg"

        response = requests.get(img_url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
        else:
            return False

    except Exception as e:
        driver.quit()
        print(e)
        return False


def youtube_to_mp4(url, output_path='downloads/Videos'):
    try:
        yt = YouTube(url)
        video_stream = yt.streams.filter(res="1080p", mime_type="video/mp4", progressive=False).first()
        audio_stream = yt.streams.filter(only_audio=True, mime_type="audio/mp4").first()

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        print(f"Downloading video: {yt.title}")
        filename = f"{uuid.uuid4()}.mp4"
        video_path = os.path.join(output_path, "video.mp4")
        audio_path = os.path.join(output_path, "audio.mp4")
        final_path = os.path.join(output_path, filename)

        video_stream.download(output_path=output_path, filename="video.mp4")
        audio_stream.download(output_path=output_path, filename="audio.mp4")

        print("Merging video and audio...")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            final_path
        ])

        os.remove(video_path)
        os.remove(audio_path)

        print(f"Done! File saved as: {final_path}")

        return f"{output_path}/{filename}"

    except Exception as e:
        print(e)
        return False


def download_facebook_images(post_url):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)
        driver.get(post_url)

        time.sleep(3)
        img_elements = driver.find_elements(By.XPATH, '//img[contains(@src, "scontent")]')
        image_urls = [img.get_attribute("src") for img in img_elements]

        if not image_urls:
            print("Keine Bilder gefunden.")
            return

        if len(image_urls) > 1:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for idx, url in enumerate(set(image_urls)):
                    img_data = requests.get(url).content
                    zip_file.writestr(f"bild_{idx + 1}.jpg", img_data)
                    print(f"Bild {idx + 1} hinzugefügt: {url}")

            # ZIP-Datei speichern
            filename = f"downloads/Images/{uuid.uuid4()}.zip"
            with open(filename, "wb") as f:
                f.write(zip_buffer.getvalue())

            return filename

        else:
            new_filename = f"downloads/Images/{uuid.uuid4()}.jpg"
            with open(new_filename, "wb") as f:
                f.write(requests.get(image_urls[0]).content)

            return new_filename


    except Exception as e:
        print(f"Fehler bei Bilder {e}")
        driver.quit()
        return


def download_facebook_reels(url):
    filename = f'downloads/Videos/{uuid.uuid4()}.mp4'
    ydl_opts = {
        'outtmpl': filename
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return filename


def get_facebook_profile_picture(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("Profil nicht gefunden oder Zugriff verweigert.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        og_image = soup.find('meta', property='og:image')

        if og_image:
            image_url = og_image['content']
            print("Profilbild gefunden:", image_url)

            # Bild herunterladen
            image_response = requests.get(image_url)
            filename = f"downloads/Profiles/{uuid.uuid4()}.jpg"
            with open(filename, 'wb') as f:
                f.write(image_response.content)

            return filename

        else:
            print("Kein öffentliches Profilbild gefunden.")

    except Exception as e:
        print(e)


def download_media(url, title):
    end = f'.{url.split(".")[-1]}'
    filename = None
    if url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        response = requests.get(url)
        image_file = f"downloads/Images/{uuid.uuid4()}{end}"
        print(image_file)
        with open(image_file, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded image: {title}")
        filename = image_file

    elif url.endswith(('.mp4$%&$2', '.webm')):
        link = url.replace(".mp4$%&$2", "")
        filename = download_reddit_videos(link)

    else:
        print(f"Unsupported media type: {title}")

    return filename


def download_reddit_post(post_url):
    post = reddit.submission(url=post_url)
    title = post.title.replace(" ", "_").replace("/", "_")

    if post.is_video and 'reddit_video' in post.media:
        video_url = f"{post.media['reddit_video']['dash_url']}.mp4$%&$2"
        print(post.media['reddit_video'])

        return download_media(video_url, title)

    elif post.url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return download_media(post.url, title)

    elif post.is_gallery:
        zip_buffer = BytesIO()
        media_metadata = post.media_metadata
        image_urls = []
        for item in post.gallery_data["items"]:
            media_id = item["media_id"]
            if media_id in media_metadata:
                image_url = media_metadata[media_id]["s"]["u"].replace("&amp;", "&")
                image_urls.append(image_url)

        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for idx, url in enumerate(image_urls):
                img_data = requests.get(url).content
                zip_file.writestr(f"bild_{idx + 1}.jpg", img_data)
                print(f"Bild {idx + 1} hinzugefügt: {url}")

        zip_filename = f"downloads/Images/{uuid.uuid4()}.zip"
        with open(zip_filename, "wb") as f:
            f.write(zip_buffer.getvalue())

        print(f"✅ ZIP-Datei gespeichert: {zip_filename}")
        return zip_filename

    else:
        print(f"Unsupported media: {title} - {post.url}")
        return None


def get_reddit_profile_picture(url):
    try:
        if "/r/" not in url:
            username = url.split("user/")[-1].strip("/")
            user = reddit.redditor(username)

            avatar_url = user.icon_img

            response = requests.get(avatar_url)

            filename = f"downloads/Profiles/{uuid.uuid4()}.jpg"

            with open(filename, "wb") as f:
                f.write(response.content)

            return filename

        else:
            changed_url = f"{url.rstrip('/')}/about.json"
            headers = {"User-Agent": "Mozilla/5.0"}

            response = requests.get(changed_url, headers=headers)
            data = response.json()

            icon_url = data["data"].get("icon_img") or data["data"].get("community_icon")
            if icon_url:
                icon_url = icon_url.split("?")[0]

                img_response = requests.get(icon_url)
                subreddit_filename = f"downloads/Profiles/{uuid.uuid4()}.jpg"

                with open(subreddit_filename, "wb") as f:
                    f.write(img_response.content)

                return subreddit_filename
            else:
                print("Kein Profilbild gefunden.")
                return False



    except Exception as e:
        print(e)
        return None


def download_pin_image(url):

    filename = f"downloads/Images/{uuid.uuid4()}.jpg"
    print(filename)
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    return filename


def download_pinterest_video(video_url):
    print(f"🎥 Lade Video herunter mit yt-dlp: {video_url}")
    filename = f'downloads/Videos/{uuid.uuid4()}.mp4'
    ydl_opts = {
        'outtmpl': filename,
        'merge_output_format': 'mp4',
        'quiet': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    print("✅ Video fertig")
    return filename


def get_pinterest_media(pinterest_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(pinterest_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    filename = None
    video_found = False

    video_tag = soup.find("video")
    if video_tag and video_tag.get("src"):
        video_found = True
        video_url = video_tag["src"]
        print("🎬 Video gefunden")
        filename = download_pinterest_video(video_url)


    img_tag = soup.find("img", {"src": re.compile(r'^https://i\.pinimg\.com')})
    if img_tag and img_tag.get("src") and not video_found:
        image_url = img_tag["src"]
        print("🖼️ Bild gefunden")
        filename = download_pin_image(image_url)

    return filename
    print("⚠️ Kein Bild oder Video gefunden")


def download_profile_picture_pinterest(profile_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(profile_url, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")

        # Suche nach Profilbild
        img_tag = soup.find("img", {"src": re.compile(r'https://i\.pinimg\.com/.*\.jpg')})
        if img_tag and img_tag.get("src"):
            img_url = img_tag["src"]
            filename = f"downloads/Profiles/{uuid.uuid4()}.jpg"
            print(f"🖼️ Profilbild gefunden: {img_url}")

            # Download
            img_data = requests.get(img_url).content
            with open(filename, "wb") as f:
                f.write(img_data)
            print(f"✅ Gespeichert als {filename}")
            return filename

        else:
            print("⚠️ Kein Profilbild gefunden")
            return None

    except Exception as e:
        print(e)
        return None


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


reddit = praw.Reddit(
    client_id='ueIZdyYqPDQsm8nywfplYQ',
    client_secret='40L4TUjnozo8ldmGC1BM7M2U3VMClQ',
    user_agent='script:media.downloader:v1.0 (by u/Abdul_TikTok314 )'
)


@app.route("/<platform>")
def platforms(platform):
    if platform in ["instagram", "facebook", "pinterest", "reddit", "youtube", "twitter", "tiktok", "faq"]:
        return render_template(f"{platform}.html")

    else:
        return render_template("404.html")


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.route("/<path:filename>")
def download_file(filename):
    new_filename = filename.split("downloads/")[-1]
    return send_from_directory("downloads", new_filename, as_attachment=True)



@app.route("/download/<platform>", methods=["POST"])
def download(platform):
    link = request.form.get("link")
    format = request.form.get("format")

    all_functions = {"insta_profile_picture": download_instagram_profile_picture, "yt_mp4": youtube_to_mp4,
                     "tik_profile_picture": download_tiktok_profile_picture, "insta_reels": insta_download_reel,
                     "tik_videos": download_tiktok, "yt_mp3": youtube_to_mp3,
                     "insta_photos": download_insta_images, "twitter_videos": download_twitter_videos,
                     "twitter_profile_picture": get_twitter_profile_picture, "face_profile_picture": get_facebook_profile_picture,
                     "face_reels": download_facebook_reels, "face_photos": download_facebook_images, "reddit_profile_pic": get_reddit_profile_picture,
                     "reddit_photos": download_reddit_post, "pin_profile_pic": download_profile_picture_pinterest,
                     "pin_media": get_pinterest_media}

    if format in all_functions:
        filename = all_functions[format](link)

        if not filename:
            return render_template("error.html")

        return redirect(url_for("download_file", filename=filename))


    print(f"Download requested for {platform} with username: {link} and format: {format}")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
