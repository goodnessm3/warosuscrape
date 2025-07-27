Gradually scrapes all vtuber soundposts from warosu, starting at a given date and working backwards.

Script should be scheduled with a cron job:

```commandline
0 */4 * * * cd /media/1tbgreen/warosu && /usr/bin/python3 -u /media/1tbgreen/warosu/warosuScraper.py >> /media/1tbgreen/warosu/log.txt 2>&1
```



