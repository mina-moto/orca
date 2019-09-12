import json

def changeMessage(motivationLevel,motivationURL):

    message ="#Level:" + str(motivationLevel) + "です。<br><img src= '" + str(motivationURL) + "'width='200px'>"
    print(message)
    return message

def changetitle(targetName):
    titleName = str(targetName)+"さんのモチベーションレベルは"
    return titleName
