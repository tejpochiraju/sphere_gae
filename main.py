"""`main` is the top level module for your Bottle application."""

# import the Bottle framework
from bottle import Bottle, request, template, static_file, error
import json
# from google.appengine.api import users

# Create the Bottle WSGI application.
bottle = Bottle()
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

interviews = json.load( open('data/interviews.json', 'rb') )
questions = json.load( open('data/questions.json', 'rb') )
designChallenge = json.load( open('data/designchallenge.json', 'rb') )

sortedStakeholders = {}

#Generate lists for use
for stakeholder in interviews:
    interviewNum = int(interviews[stakeholder]['metadata']['Interview Number'][0])
    sortedStakeholders[interviewNum] = (stakeholder, interviews[stakeholder]['metadata']['Confidentiality'][0])

sectors = ['Air', 'Energy', 'Food', 'Waste', 'Water']

orgtypes = ['For Profit', 'Startup', 'Funder', 'Research', 'Individual', 'Not-for-Profit', 'Government', 'Academia']

qorder = ['1a', '1b', '2a', '2b', '3', '4a', '4b', '4c', '4d', '4e', '4f', '5a', '5b', '6a', '6b', '6c', '6d', '7a',
'7b', '7c', '7d', '8a', '8b', '8c', '8d', '8e', '9a', '9b', '10a', '10b', '10c', '10d', '10e', '10f', '11a', '11b', '11c',
'12a', '12b', '12c', '13a', '13b', '13c', '13d', '13e', '13f', '13g', '13h', '13i', '14a', '14b']

# metadata_tags = ['Organisation', 'Name(s) of Interviewee(s)', 'Sector', 'Type', 'Interview Number', 'Date and Time', 'Duration',
# 'Orator', 'Documentor', 'Venue', 'Interview Code']

#Short list of tags
metadata_tags = ['Organisation', 'URL', 'Name(s) of Interviewee(s)', 'Sector', 'Type', 'Interview Number', 'Interview Code']


# Define an handler for the root URL of our application.
@bottle.get('/') # or @route('/login')
def index():
    output = template('templates/index', designChallenge=designChallenge, stakeholders=sortedStakeholders, get_url=bottle.get_url)
    return output

@bottle.post('/')
def doSearch():
    phrase = request.forms.get('phrase')
    count, results = search(interviews, phrase)
    if phrase:
        output = template('templates/search', phrase=phrase, count=count, qorder=qorder, questions=questions, results=results, interviews=interviews, get_url=bottle.get_url)
        return output
    else:
        return "<p>Search failed.</p>"

@bottle.route('/search/<phrase>')
def doSearch2(phrase='Jaaga'):
    count, results = search(interviews, phrase)
    if phrase:
        output = template('templates/search', phrase=phrase, count=count, qorder=qorder, questions=questions, results=results, interviews=interviews, get_url=bottle.get_url)
        return output
    else:
        return "<p>Search failed.</p>"


@bottle.route('/stakeholder/<name>')
def showStakeholder(name='Saahas'):
    responses = interviews[name]['responses']
    count = len(responses)
    output = template('templates/stakeholder', name=name, count=count, tags=metadata_tags, metadata=interviews[name]['metadata'], qorder=qorder, questions=questions, responses=responses, get_url=bottle.get_url)
    return output

@bottle.route('/questions')
@bottle.route('/questions/')
def showQuestionList():
    output = template('templates/questions', qorder=qorder, questions=questions, get_url=bottle.get_url)
    return output

@bottle.route('/question/<qnumber>')
def showQuestion(qnumber='1a'):
    results = {}
    count = 0
    for name in interviews:
        if qnumber in interviews[name]['responses']:
            for response in interviews[name]['responses'][qnumber]:
                if qnumber not in results:
                    results[qnumber] = {}
                if name not in results[qnumber]:
                    results[qnumber][name] = []
                results[qnumber][name].append(response)
                count += 1
    output = template('templates/search', phrase="Question "+qnumber, count=count, qorder=qorder, questions=questions, results=results, interviews=interviews, get_url=bottle.get_url)
    return output

@bottle.route('/sectors')
@bottle.route('/sectors/')
def showSectorList():
    output = template('templates/sectors', qorder=qorder, sectors=sectors, get_url=bottle.get_url)
    return output

@bottle.route('/sector/<sector>')
def showSector(sector='Waste'):
    results = {}
    count = 0
    for name in interviews:
        if interviews[name]['metadata']['Sector'][0].lower() == sector.lower():
            for qnumber in qorder:
                if qnumber in interviews[name]['responses']:
                    for response in interviews[name]['responses'][qnumber]:
                        if qnumber not in results:
                            results[qnumber] = {}
                        if name not in results[qnumber]:
                            results[qnumber][name] = []
                        results[qnumber][name].append(response)
                        count += 1
    output = template('templates/search', phrase="Sector "+sector, count=count, qorder=qorder, questions=questions, results=results, interviews=interviews, get_url=bottle.get_url)
    return output

@bottle.route('/types')
@bottle.route('/types/')
def showTypeList():
    output = template('templates/types', qorder=qorder, types=orgtypes, get_url=bottle.get_url)
    return output

@bottle.route('/type/<type>')
def showType(type='For Profit'):
    results = {}
    count = 0
    for name in interviews:
        if interviews[name]['metadata']['Type'][0].lower() == type.lower():
            for qnumber in qorder:
                if qnumber in interviews[name]['responses']:
                    for response in interviews[name]['responses'][qnumber]:
                        if qnumber not in results:
                            results[qnumber] = {}
                        if name not in results[qnumber]:
                            results[qnumber][name] = []
                        results[qnumber][name].append(response)
                        count += 1
    output = template('templates/search', phrase="Organisation type: "+type, count=count, qorder=qorder, questions=questions, results=results, interviews=interviews, get_url=bottle.get_url)
    return output

@bottle.route('/static/<filename>', name='static')
def server_static(filename):
    return static_file(filename, root='static')

# Define an handler for 404 errors.
@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL. Click <a href="/"">here</a> to return to the landing page.'


def search(interviews, phrase):
    results = {}
    count = 0
    for qnumber in qorder:
        for name in interviews.keys():
            code = interviews[name]['metadata']['Interview Code'][0] + '-' + qnumber
            if qnumber in interviews[name]['responses']:
                rcount = 0
                for response in interviews[name]['responses'][qnumber]:
                    rcount += 1
                    code = code + '-' + str(rcount)
                    if all(word in response.lower() or word in questions[qnumber] or word in code for word in phrase.lower().split()):
                        if qnumber not in results:
                            results[qnumber] = {}
                        if name not in results[qnumber]:
                            results[qnumber][name] = []
                        results[qnumber][name].append(response)
                        count += 1
    return(count, results)
