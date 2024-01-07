import requests,json, re
from datetime import datetime,timezone,timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
import os
load_dotenv()

interval_days=8

def filter_chars(text):
    input=str(text)
    special_chars="',!/()[+].{}:-_=>—@$£€₹￥’"
    return "".join([c for c in input if(c.isprintable() and (c.isalnum() or c.isspace() or (c in special_chars)))])
#     return "".join([c for c in input if(c.isalnum() or c.isspace() or (c in special_chars))])

def get_msg(ctf,i,starttime):
  return f"""
{filter_chars(i)}. **[{filter_chars(ctf['title'])}]({filter_chars(ctf['url'])})**
 - **Format:** {filter_chars(ctf['format'])} , **Weight:** {filter_chars(ctf['weight'])}
 - **Start:** {filter_chars(starttime)}
 - **Prizes: check on [CTFtime]({filter_chars(ctf['ctftime_url'])})**
 - **Description:** {filter_chars(ctf['description'][:100])}..."""

def get_embed(ctf,i,starttime):
       return {
  #     'title': f"""**[{filter_chars(ctf['title'])}]({filter_chars(ctf['url'])})**""",
  'title': filter_chars(ctf['title']),
  'url': filter_chars(ctf['url']),
  'description': f"""
- **Format:** {filter_chars(ctf['format'])} , **Weight:** {filter_chars(ctf['weight'])}
- **Start:** {filter_chars(starttime)}
- **Prizes: check on [CTFtime]({filter_chars(ctf['ctftime_url'])})**
- **Description:** {filter_chars(ctf['description'][:100])}..."""
  ,'thumbnail': {
    'url': ctf['logo'],
  }}

def ctftime_job():
  url=f'https://ctftime.org/api/v1/events/?limit={interval_days}' # 1 CTF daily max
  data=requests.get(url,headers={'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'})
  ctfs=json.loads(data.text)
  embeds=[]
  i=1
  ctf_events_message = f"""**Upcoming CTFs(weekly):**"""
  for ctf in ctfs:
    start=datetime.fromisoformat(ctf["start"])
    if(ctf["onsite"]==False and start-datetime.now(timezone.utc)<timedelta(days=interval_days)):
      #and ctf['restrictions']=='Open'/'Academic' 

      start+=timedelta(hours=+5.5) # IST
      starttime=start.strftime("%a %d %b %I:%M %p IST")
      
      msg=get_msg(ctf,i,starttime)
      embeds.append(get_embed(ctf,i,starttime))

      ctf_events_message+=msg
      i+=1

  webhook_url = os.getenv("WEBHOOK_URL")
  headers = {'Content-Type': 'application/json'}

  webhook_data = {
  'username': 'CTFtime bot',
  # 'content': ctf_events_message,
  'content': '**Upcoming CTFs(weekly):**',
      'embeds': embeds
  }
  response = requests.post(webhook_url, data=json.dumps(webhook_data), headers=headers)

# print(ctf_events_message)
# print(ctfs)
ctftime_job()

scheduler = BlockingScheduler()
# every Friday at 7 PM
scheduler.add_job(ctftime_job, trigger=CronTrigger(hour=19, day_of_week=4)) # 6=Sunday
# scheduler.add_job(ctftime_job, trigger=CronTrigger(hour=17, minute=38, day_of_week=6)) 
scheduler.start()