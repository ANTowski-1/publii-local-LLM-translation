from ollama import chat, ChatResponse
import yaml
import argparse
import sqlite3

parser = argparse.ArgumentParser(description="Automatily translate Publii-made websites, using a localy hosted LLM through ollama.")
parser.add_argument('-c', '--config', help='Select path to your YAML configuration file.', default="config.yml", type=str)
parser.add_argument('-d', '--DB', help='Select path to the programs DB.', default="cashedDB.sqlite", type=str)
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


progDB = sqlite3.connect(args.DB)
progCursor = progDB.cursor()


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
    orgRecord = orgCursor.fetchall()
    targCursor.execute('SELECT * FROM posts WHERE id is ?', str(i))
    targRecord = orgCursor.fetchall()
    if targRecord != orgRecord:
        message = 'Translate this html from' + orgLang + ' to ' + targLang + ' , while preserving the, style and the vibe of my writing. \
        DO NOT CHANGE ANY OF THE HTML FORMATING! Do not add any things apart from the raw translated data. ' \
        + str(orgRecord[0][4])
        response: ChatResponse = chat(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': message,
                },
            ],
            stream=True,
        )

        for chunk in response:
            print(chunk['message']['content'], end='', flush=True)
        print()
        
        targCursor.execute('INSERT * TO posts WHERE id IS ?')



