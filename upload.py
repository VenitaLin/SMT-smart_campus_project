import requests
import json

url_postprof = 'https://smt203-project-team1.herokuapp.com/postprofessor'
url_postcourse = 'https://smt203-project-team1.herokuapp.com/postcourse'
url_postprofcourse = 'https://smt203-project-team1.herokuapp.com/postprofcourse'

#post course
with open('data.txt') as f:
    f.readline()
    for l in f:
        l = l.rstrip('\n').split('|')
        r = requests.post(url=url_postcourse,json={"cid":l[3],'name':l[2],'school':l[0]})


#post professor
with open('data.txt') as f:
    f.readline()
    for l in f:
        l = l.rstrip('\n').split('|')
        r = requests.post(url=url_postprof,json={'name':l[1]})


#post prof_course
with open('data.txt') as f:
    f.readline()
    for l in f:
        l = l.rstrip('\n').split('|')
        r = requests.post(url=url_postprofcourse,json={'pname':l[1],'cname':l[2]})