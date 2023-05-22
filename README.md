# Automating the scraping of Reddit videos and uploading to YouTube
Can be done using Python and some useful libraries. 
- First, Selenium is used to scrape the page source, with the ability to automatically scroll down. 
- Second, BS4 or BeautifulSoup can be used for easy regex searching of the title, video URL, and upvotes. 
- After that, the video and audio can be downloaded from the URL using urllib3. 
- To combine the video and audio into a single file, they are merged because Reddit has separated them into two files. 
- The merged video can then be uploaded to a specific YouTube channel using YouTube API 3. A helpful video tutorial for this task can be found at https://youtu.be/eq-mjehACe4. 
- Lastly, the scraped data can be updated to a .csv file by using Pandas. 
- This entire process becomes easier with the help of [my best friends](https://chat.openai.com/).
- see demo on Youtube : https://www.youtube.com/watch?v=NJWPkq1pNwA)
