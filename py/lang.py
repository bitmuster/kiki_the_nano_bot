# -*- encoding: utf-8 -*-

if Controller.isDebugVersion(): print("[lang.py]")

Controller.language = "english"

lang_list = [  "dutch", "english", "euskara", "francaise", "german",  "portuguese", "spanish", "swedish", ]
lang = {}
for langName in lang_list:
    exec(compile(open(kikipy_path + os.path.sep + "lang" + os.path.sep + langName + ".py", "rb").read(), kikipy_path + os.path.sep + "lang" + os.path.sep + langName + ".py", 'exec'))

def getLocalizedString(text):
  if text in lang[Controller.language]:
    return lang[Controller.language][text]
  else:
    return text
  
Controller.getLocalizedString = getLocalizedString

del getLocalizedString
