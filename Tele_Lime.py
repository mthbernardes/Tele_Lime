#!/usr/bin/env python
# -*- coding: utf-8 -*-

from daemon import Daemon
from BeautifulSoup import BeautifulSoup
import requests,xmltodict,telepot,time,os,sys,datetime

class daemon_server(Daemon):
    def run(self):
        main()

def get_conf():
    from ConfigParser import ConfigParser
    config = ConfigParser()
    config.read('etc/Tele_Lime.conf')
    telegram_api = config.get('Telegram','api')
    group_id = config.get('Telegram','group_id')
    admins = config.get('Telegram','admins')
    lime_api = config.get('Lime','api')
    admins = config.get('Telegram','admins')
    return telegram_api,group_id,admins,lime_api

def api_request(mode,action):
    url = 'https://one.limestonenetworks.com/webservices/clientapi.php?key=%s&mod=%s&action=%s' % (lime_api, mode, action)
    conn = requests.get(url)
    return conn.content

def tickets():
    count = 0
    response = api_request('support','listtickets')
    infos =  xmltodict.parse(response)
    for info in infos['tickets']['ticket']:
        if info['status'] != 'closed':
            status = info['status']
            user_id = info['user_id']
            username =  info['username']
            subject = BeautifulSoup(info['subject']).text
            description = BeautifulSoup(info['description']).text
            bot.sendMessage(chat_id, 'Status: '+status+'\nUser ID: '+user_id+'\nUsername: '+username+'\nSubject: '+subject+'\nDescription: '+description)
            count += 1
    if count == 0:
            bot.sendMessage(chat_id, 'Relaxa nao tem tickets :D')
def view_ticket(ticket_number):
    response = api_request('support','viewticket&ticket='+str(ticket_number))
    infos =  xmltodict.parse(response)
    ticket = infos['ticket']
    ticket_ID = ticket['@id']
    opened = datetime.datetime.fromtimestamp(int(ticket['opened'])).strftime('%d-%m-%Y %H:%M:%S')
    status = ticket['status']
    username = ticket['username']
    subject = BeautifulSoup(ticket['subject']).text
    description = BeautifulSoup(ticket['description']).text
    ticket_type = ticket['type']
    bot.sendMessage(chat_id, 'ID: '+ticket_ID+'\nType: '+ticket_type+'\nOpened at:',opened,'\nStatus: '+status+'\nUsername: '+username+'\nSubject: '+subject+'\nDescription: \n'+description)
    for response in ticket['responses']['response']:
        time_response = datetime.datetime.fromtimestamp(int(response['timestamp'])).strftime('%d-%m-%Y %H:%M:%S')
        username_response = response['name']
        comment_response = BeautifulSoup(response['comment']).text
        bot.sendMessage(chat_id, 'Response time:' , time_response,'\nUsername: '+username_response+'\nAnswer: \n'+comment_response)


def server_list():
    response = api_request('servers','list')
    infos =  xmltodict.parse(response)
    for info in infos['servers']['server']:
            server_id = info['@id']
            name = info['displayname']
            status = info['status']
            os = info['operatingsystem']
            public_ip = info['publicip']
            private_ip = info['privateip']
            bandwitch = info['bandwidth']['actual']['percentage']+'%'
            bot.sendMessage(chat_id, 'Server ID:: '+server_id+'\nName: '+name+'\nStatus: '+status+'\nOS: '+os+'\nPublic IP: '+public_ip+'\nPrivate IP:'+private_ip+'\nBandwitch: '+bandwitch)

def graph(server):
    api_request('servers','bwgraph&server_id='+server)
    file_png = open(server+'.png','wb')
    file_png.write()
    file_png.close()
    file_png = open(server+'.png','rb')
    bot.sendPhoto(chat_id,file_png)
    os.system('rm '+server+'.png')

def actions(command):
    command = command.split()
    if command[0] == '/ticket':
        if len(command) > 1:
            view_ticket(command[1])
        else:
            tickets()

    elif command[0] == '/servers':
        server_list()

    elif command[0] == '/graph':
        if len(command) > 1:
            graph(command[1])

def handle_message(msg):
    try:
        username = msg['from']['username']
    except:
        username = ''
    content_type, chat_type, chat_id = telepot.glance2(msg)
    if chat_type == 'group' and username in admins:
        if content_type is 'text':
            command = msg['text'].lower()
            actions(command)
    else:
        bot.sendMessage(chat_id, 'Desculpe nao tenho permissao para falar com voce!')

def main():
    bot.notifyOnMessage(handle_message)
    while 1:
        time.sleep(10)

telegram_api,chat_id,admins,lime_api = get_conf()
admins = admins.split(',')
bot = telepot.Bot(telegram_api)

daemon_service = daemon_server('/var/run/Tele_Lime.pid')
if len(sys.argv) >= 2:
    if sys.argv[1] == 'start':
        daemon_service.start()

    elif sys.argv[1] == 'stop':
        daemon_service.stop()

    elif sys.argv[1] == 'restart':
        daemon_service.stop()
        daemon_service.start()

    elif sys.argv[1] == 'status':
        daemon_service.is_running()
else:
    print 'Usage:',sys.argv[0],'star | stop | restart | status'
