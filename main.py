from ollama import chat, ChatResponse
import yaml
import argparse
import sqlite3
from time import sleep


def pushTranslated(transData, id):
    targCursor.execute('SELECT * FROM posts WHERE id is ?', str(id))
    if [list(row) for row in targCursor.fetchall()] == "[]":
        targCursor.execute('INSERT INTO posts VALUES (?,?,?,?,?,?,?,?,?,?)', [str(transData[0][0]), str(transData[0][1]), str(transData[0][2]), str(transData[0][3]), \
                    str(transData[0][4]), str(transData[0][5]), str(transData[0][6]), str(transData[0][7]), str(transData[0][8]), str(transData[0][9])])
    else:
        targCursor.execute('UPDATE posts SET text = ?, modified_at = ?, status = ? WHERE id = ?', [str(transData[0][4]), str(transData[0][7]), str(transData[0][8]), str(id)])
        print("Puted the query into the DB")
    return


parser = argparse.ArgumentParser(description="Automatily translate Publii-made websites, using a localy hosted LLM through ollama.")
parser.add_argument('-c', '--config', help='Select path to your YAML configuration file.', default="config.yml", type=str)
parser.add_argument('-d', '--DB', help='Select path to the programs DB.', default="cashedDB.sqlite", type=str)
parser.add_argument('--debug', help='Enable debuging mode.', action='store_true')
args = parser.parse_args()

try:
    config = yaml.safe_load(open(args.config))
    print(config)
except yaml.YAMLError as exc:
    print(exc)

orgLang = str(config.get('language').get('orginal'))
targLang = str(config.get('language').get('target'))
orgPath = str(config.get('projectPath').get('orginal'))

targPath = str(config.get('projectPath').get('target'))
model = str(config.get('model'))

print(orgLang)
print(targLang)
print(orgPath)
print(targPath)

cashedDB = sqlite3.connect(args.DB)
cashedCursor = cashedDB.cursor()

orgDB = sqlite3.connect(str(orgPath + '/input/db.sqlite'))
orgCursor = orgDB.cursor()

targDB = sqlite3.connect(str(targPath + '/input/db.sqlite'))
targCursor = targDB.cursor()

orgCursor.execute('SELECT id FROM posts ORDER BY id DESC LIMIT 1')
postsNum = orgCursor.fetchall()[0][0]
print(postsNum)

i = 0

while i < postsNum:
    i = i + 1
    orgCursor.execute('SELECT * FROM posts WHERE id is ?', str(i))
    orgRecord = [list(row) for row in orgCursor.fetchall()]
    cashedCursor.execute('SELECT * FROM posts WHERE id is ?', str(i))
    cashedRecord = [list(row) for row in cashedCursor.fetchall()]
    if cashedRecord != orgRecord:

        message = 'Translate this html from ' + orgLang + ' to ' + targLang + ' , while preserving the, style and the vibe of my writing.\
 DO NOT CHANGE ANY OF THE HTML FORMATING! Do not add any things apart from the raw translated data.\
 Do not include the orginal data, and do not add text formating stating what file type it is — response should only contain plain translated part.\
 If you are greeted with a longer JSON, only translate the "content" parts, but output the whole JSON string.' \
        + str(orgRecord[0][4])
        if args.debug == True:
            print("Promp: "+message)
        
        response: ChatResponse = chat(  
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': message,
                },
            ],
        )

        
        print("Translation of post/page, ID = " + str(i))
        print(response['message']['content'])
        translation = str(response['message']['content'])
        cashedRecord = orgRecord
        targRecord = orgRecord
        targRecord[0][4] = translation
        pushTranslated(targRecord, i)

print("Everything translated!")
print("Terminating program!")

exit

