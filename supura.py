import discord
import urllib.request
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib

urllib.request.urlretrieve('https://splatoon.caxdb.com/schedule2.cgi','origin.txt')
import re

#function that get days and times when the match will start, if 'line' is about date.
def date_getter(line):
    if bool(re.search('(\d+)/(\d+)',line)):
        start_day = re.search('(\d+)/(\d+)',line).group()
        start_time = re.search('(\d+):(\d+)',line).group()
        return {'start_day':start_day,'start_time':start_time}
    
    return None

def main(input_str):
    dates = []
    stages =[]

    genre = input_str.split('/')[0]
    rule = input_str.split('/')[1]

    fr_origin = open('origin.txt','r')
    fw_scraped_1 = open('scraped_1.txt','w')
    write_switch = False

    for line in fr_origin:
        line = re.sub('<[^>]*>','',line)

        if bool(date_getter(line)) or write_switch:
            write_switch = True
            fw_scraped_1.write(line)
        
    fr_origin.close()
    fw_scraped_1.close()


    fr_scraped_1 = open('scraped_1.txt','r')
    fw_scraped_2 = open('scraped_2.txt','w')

    for line in fr_scraped_1:
        if bool(date_getter(line)):
            time = line

        if bool(re.search(genre + '.' + rule,line)):
            fw_scraped_2.write(time)
            dates.append(time.strip('\n'))
            
            fw_scraped_2.write(line)#genre
            
            fr_scraped_1.readline()#(blank-reading)
            
            stage_1 = fr_scraped_1.readline()#stage1
            fw_scraped_2.write(stage_1)
            stage_2 = fr_scraped_1.readline()#stage2
            fw_scraped_2.write(stage_2)
            
            stages.append(stage_1.strip('\n') + '/\n' + stage_2.strip('\n'))

            
    fr_scraped_1.close()
    fw_scraped_2.close()

    #get 'fw_scraped_2.txt' : information about date and stages of the match that you want to play.
    #get dates[], stages[] : date-array and stages-array both has same length. these were made based on 'fw_scraped_2.txt'.

    plt.rcParams['font.family'] ='Hiragino Maru Gothic Pro'#font

    days = []
    colored_num = []
    color_list = ['#eee']*12
    stage_list = ['']*12

    for date in dates:
        start_time = date_getter(date)['start_time']
        #ex) '17:00', get start time from date line.
        start_day = date_getter(date)['start_day']
        #ex) '06/30', get start day from date line.
        
        colored_num.append(int((int(start_time.strip(':00'))-1)/2))
        #ex)'13:00' → '13'→ ((13-1)/2) → 6, this number represents colored part of pie chart.

        days.append(start_day)

    day_str = days[0] + '~' + days[-1]
    #connect the top and end elements of days array.
    #ex)[07/12, 07/12, 07/13] → '07/12 ~ 07/13'

    for n in colored_num:
        color_list[n] = '#EC48AF'
        stage_list[n] = stages.pop(0)


    x = np.array([1]*24)
    y = np.array([1]*12)

    label = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

    #igfont = {'family':'IPAexGothic'}


    plt.figure(figsize=(7, 8), dpi=95)
    plt.pie(x,labels=label,counterclock=False,startangle=97.5,colors=['1'],textprops={'color': "#000", 'weight': "bold"},labeldistance=1.05)
    plt.pie(y,labels=stage_list,counterclock=False,startangle=75,colors = color_list,labeldistance=0.4,textprops={'color': "#000", 'weight': "bold",'size': "12"},wedgeprops={'linewidth': 1,'edgecolor':"gray"})
    plt.title(genre +'-'+ rule + '\n(' + day_str + ')',fontsize = 18, fontweight = 'bold', color = '#000')

    plt.savefig('schedule.png', bbox_inches='tight')


#plt.show()

#discobot
TOKEN = 'NzI3ODE3MjIxMzU4NzQ3NzYw.XvxbHA.guYOJ1BBgIobuZg-9NLeh6Nzi_8'

client = discord.Client()

@client.event
async def text(message):
    schedule_text = open('scraped_2.txt','r')
    lines = ''
    for line in schedule_text:
        lines += line

    channel = message.channel
    await channel.send('```\n' + lines + '\n```')
    schedule_text.close()


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if bool(message.content.endswith('ikachan')):
        channel = message.channel
        main(message.content.strip('ikachan'))
        await channel.send(file=discord.File('schedule.png'))

    elif bool(message.content.endswith('ikachan-text')):
        channel = message.channel
        main(message.content.strip('ikachan-text'))
        await text(message)



# async def on_message(message):
#     if message.author.bot:
#         return

#     if message.content == 'supura':
#         channel = message.channel
#         await channel.send(file=discord.File('schedule.png'))
        
client.run(TOKEN)
