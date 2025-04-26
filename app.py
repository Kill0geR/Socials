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
from selenium.webdriver.common.by import By
import subprocess


def youtube_to_mp3(url):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        video_file = video.download(output_path="downloads", filename='temp_video')

        get_song_name = f'downloads/{uuid.uuid4()}.mp3'
        video_clip = AudioFileClip(video_file)
        video_clip.write_audiofile(get_song_name)

        os.remove(video_file)
        return get_song_name
    except Exception as e:
        print(e)
        return False

    print("Conversion completed successfully!")


def download_insta_images(post_url):
    try:
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

        zipname = f"{real_folder}/{uuid.uuid4()}.zip"

        with zipfile.ZipFile(zipname, 'w') as zipf:
            for file in valid_files:
                zipf.write(file, arcname=file.split('/')[-1])
                os.remove(file)

        os.rmdir(str(target_file))

        return zipname

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
        change_dir = f"downloads/TikTok_Video"
        os.chdir(change_dir)

        pyk.specify_browser('chrome')

        pyk.save_tiktok(url, True)
        filename = f"{change_dir}/{os.listdir()[0]}"
        os.chdir("../..")
        return filename

    except Exception as e:
        print(e)
        os.chdir("../..")


def download_tiktok_profile_picture(link):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
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


def youtube_to_mp4(url, output_path='downloads'):
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

        return f"downloads/{filename}"

    except Exception as e:
        print(e)
        return False


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


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
                     "insta_photos": download_insta_images}

    if format in all_functions:
        filename = all_functions[format](link)
        print(filename)
        return redirect(url_for("download_file", filename=filename))


    print(f"Download requested for {platform} with username: {link} and format: {format}")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
