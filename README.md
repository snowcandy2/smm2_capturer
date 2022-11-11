# smm2_capturer

For live stream of the game Super Mario Maker 2, which can show the level name, versus win rate, deaths, level information...

Special thanks to tgrcode.com which provides the API of Super Mario Maker 2, it can show the detailed level info. 

## Install

Apart from what `requirements.txt` that you should install, you should also install tesseract OCR to make recognizations and make configs on tesseract. Also, <a href="//obsproject.com/forum/resources/obs-virtualcam.539/">OBS Virtualcam</a> is required if you want to do live stream. The virtual camera that comes with OBS itself cannot be turned on in some systems. 

Moreover, you need to install MySQL (used in this version to record information such as course ID), create a database (the database name can be changed in jxmai.py) and run the SQL file I provided in the database (not uploaded yet). You don't have to install MySQL on a local PC.

## Configure

First, open OBS and setup virtualcam, then open `camera.py`, enter the correct virtualcam ID. If you are not sure, you can change the camera ID and run `camera.py`. It will show the current camera. 

Then run `jxmai.py`.

***Since this plugin was once used by me personally, I coded terribly. I will refine it later.***

## Successful Use Cases

I successfully deployed this stuff to <a href="//live.bilibili.com/14065607">my friend's stream room</a> (her MM2 id is `maolizi`), and she can show her deaths to viewers when grinding levels. It was a bit unstable to use this in CN for `tgrcode` is somehow unavailable in CN. To solve this problem, I proxied `tgrcode` and <a href="//yohane.cc/mm2/user_info/MC0GSVRMF">made it available in CN w/o using VPN</a>. 

To be continued...
