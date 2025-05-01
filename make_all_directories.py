import os

os.mkdir("downloads")

for each in ["Audios", "Images", "Profiles", "Reels", "TikTok_Video", "Videos"]:
    os.mkdir(f"downloads/{each}")
