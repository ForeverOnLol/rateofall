import configparser

config = configparser.ConfigParser()
config.read('config.ini')
max_word_count_roa = int(config['ROA']['MaxWordCount'])
max_word_count_deb = int(config['DEB']['MaxWordCount'])
unsplash_api_key = str(config['DEFAULT']['UnsplashApiKey'])
is_desktop_exist = True if config['DEFAULT']['DesktopUI'] == 'yes' else False
bot_link = config['DEFAULT']['BotLink']
send_word_seconds = int(config['ROA']['SendWordSeconds'])
personal_word_count = int(config['ROA']['PersonalWordCount'])

sec_between_answers = int(config['DEB']['SecBetweenAnswers'])
sec_to_answer = int(config['DEB']['SecToAnswer'])