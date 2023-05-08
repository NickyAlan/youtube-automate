import time
import subprocess
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib3 import PoolManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from moviepy.editor import VideoFileClip, AudioFileClip
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# scrap data
URL = 'https://www.reddit.com/r/MemeVideos/'
base_url = 'https://www.reddit.com'
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get(URL)
time.sleep(3)
driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)

# some scoll for get the newest data
print('GET THE DATA')
for scoll_time in range(2) :
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(6)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
driver.quit()
posts = soup.find_all('div', {'class': '_1oQyIsiPHYt6nx7VOmd1sz'})

# get video url from each post
max_bytes = 34275534
video_qualities = ['1080.mp4', '720.mp4', '480.mp4']
pool = PoolManager()
master_list = []
print('SCRAPING')
for post in posts :
    video_detail = {}
    # not promoted or ads
    if 'promoted' not in post.text :
        upvote = post.find('div', {'class': '_1rZYMD_4xY3gRcSS3p8ODO'}).text
        title = post.find('h3').text.strip()
        video_detail['upvote'] = upvote
        video_detail['title'] = title
        # find video url
        if post.find('shreddit-player') :
            video_id = post.find('shreddit-player')['preview'].split('/')[-2]
            video_url = f'https://v.redd.it/{video_id}/DASH_'
            for video_quality in video_qualities :
                test_response = video_url + video_quality
                response = pool.request("GET", test_response, preload_content=False)
                status_code = response.status
                bytes = int(response.headers.get("Content-Length"))
                # if url exist and length video less than 60sec 
                if status_code == 200 and bytes < max_bytes :
                    video_url = test_response
                    video_detail['video_url'] = video_url
                    video_detail['video_sound_url'] = f'https://v.redd.it/{video_id}/HLS_AUDIO_160_K.aac'
                    break
    if len(video_detail.keys()) == 4 : 
        master_list.append(video_detail)
        print(video_detail)

# add new data to csv
data_df = pd.read_csv('youtube_shorts_videos_data.csv')
new_df = pd.DataFrame(master_list)
df = pd.concat([data_df, new_df])
df['upvote'] = df['upvote'].apply(lambda num: int(float(num[:-1])*1000) if str(num)[-1] == 'k' else int(num))
df = df.sort_values(by=['upvote'], ascending=False)
df = df.drop_duplicates()

def download_from_url(url: str, filepath: str, format: str) :
    urllib.request.urlretrieve(url, filepath + format)

def merge_video_and_audio(videopath: str, audiopath: str) :
    print(f'MERGE VIDEO AND AUDIO')
    video = VideoFileClip(videopath)
    if video.duration < 59 : # for youtube SHORTs < 60 second
        audio = AudioFileClip(audiopath)
        merge = video.set_audio(audio)
        merge.write_videofile(f'{videopath[:-4]}_merge.mp4', logger=None, verbose=False)

def upload_video(videopath: str, title: str) :
    command = f'python upload.py --file="{videopath}" --title="{title}"'
    subprocess.call(command, shell=True)
    print(f'UPLOADED | {title} {videopath} COMPLETED')

count = 1
for idx, row in df.iterrows() :
    upvote = row['upvote']
    video_url = row['video_url']
    video_sound_url = row['video_sound_url']
    name = f'videos/{upvote}_{video_url.split("/")[-2]}'
    # download video and audio
    for url in [video_url, video_sound_url] :
        if url[-4:] == '.mp4' : 
            download_from_url(url, name, '.mp4')
        else :
            download_from_url(url, name, '.mp3')
    print('DOWNLOADED')
    # merge video and audio
    merge_video_and_audio(f'{name}.mp4', f'{name}.mp3')
    # upload video
    upload_video(f'{name}_merge.mp4', row['title'])
    # remove from df so i won't upload the same video
    df = df.drop(idx)
    # check for breaking just 5 video for a day
    if count == 5 : break 
    count += 1
    # take a break for youtube new upload
    time.sleep(5)
    break

# update removing row to csv
df.to_csv('youtube_shorts_videos_data.csv', index=False)