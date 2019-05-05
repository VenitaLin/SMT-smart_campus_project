from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
# your code starts here
app = Flask(__name__)
app.debug = True

#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://smt203t1:smt203t1@localhost:5432/smt203project"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

from models import Professor, Course, Prof_Course, Review

@app.route("/postprofessor", methods=["POST"])
def create_prof():
    name = request.json["name"]
    new_prof = Professor(name=name)
    db.session.add(new_prof)
    db.session.commit()
    return jsonify("{} was created".format(new_prof))


@app.route("/postcourse", methods=["POST"])
def create_course():
    cid = request.json["cid"]
    name = request.json["name"]
    school = request.json["school"]
    new_course = Course(cid=cid, name=name, school=school)
    db.session.add(new_course)
    db.session.commit()
    return jsonify("{} was created".format(new_course))


@app.route("/postprofcourse", methods=["POST"])
def create_profcouse():
    cname = request.json["cname"]
    pname = request.json["pname"]
    new_profcourse = Prof_Course(cname=cname, pname=pname)
    db.session.add(new_profcourse)
    db.session.commit()
    return jsonify("{} was created".format(new_profcourse))


@app.route("/postreview", methods=["POST"])
def create_postreview():
    reviewer = request.json["reviewer"]
    pname = request.json["pname"]
    cname = request.json["cname"]
    score1 = request.json["score1"]
    score2 = request.json["score2"]
    score3 = request.json["score3"]
    try:
        year = request.json["year"]
    except:
        year = None
    try:
        school = request.json["school"]
    except:
        school = None
    try:
        comment = request.json["comment"]
    except:
        comment = None
    try:
        advice = request.json["advice"]
    except:
        advice = None
    new_review = Review(reviewer=reviewer, pname=pname, cname=cname, score1=score1,
                        score2=score2, score3=score3, year=year, school=school, comment=comment, advice=advice)
    db.session.add(new_review)
    db.session.commit()
    return jsonify("{} was created".format(new_review))

#######################GET Method######################################

@app.route("/getcourse",methods=["GET"])
def get_course():
    if 'cid' in request.args:
        cid = request.args.get("cid")
        course = Course.query.filter_by(cid=cid).all()
        return jsonify([c.serialize() for c in course])
    elif 'cname' in request.args:
        cname = request.args.get("cname")
        course = Course.query.filter_by(name=cname).all()
        return jsonify([c.serialize() for c in course])

@app.route("/getprofessor",methods=['Get'])
def get_professor():
    name = request.args.get("name")
    professor = Professor.query.filter(Professor.name.like('%'+name+'%')).all()
    return jsonify([p.serialize() for p in professor])
        
@app.route("/getreview", methods=["GET"])
def get_review():
    if "cid" in request.args:  # if user enter courseID
        cid = request.args.get("cid")
        course = Course.query.filter_by(cid=cid).first()
        cname = course.name
    else:  # if user enter course name
        cname = request.args.get("cname")
    if "offset" in request.args:  # if user specifiy how many records to show
        offset = request.args.get("offset")
        review = Review.query.filter_by(cname=cname).limit(offset)
        return jsonify([r.serialize() for r in review])
    else:
        review = Review.query.filter_by(cname=cname).limit(15)
        return jsonify([r.serialize() for r in review])

@app.route("/getprofcourse",methods=["GET"])
def get_profcourse():
    if "cid" in request.args:
        cid = request.args.get("cid")
        course = Course.query.filter_by(cid=cid).first()
        cname = course.name
        profcourse = Prof_Course.query.filter_by(cname=cname).all()
        return jsonify([p.serialize() for p in profcourse])
    elif "cname" in request.args:
        cname = request.args.get("cname")
        profcourse = Prof_Course.query.filter_by(cname=cname).all()
        return jsonify([p.serialize() for p in profcourse])
    elif "pname" in request.args:
        pname = request.args.get("pname")
        profcourse = Prof_Course.query.filter_by(pname=pname).all()
        return jsonify([p.serialize() for p in profcourse])


@app.route("/getmodreview", methods=["GET"])
def get_modreview():
    pname = request.args.get("pname")
    if "cname" in request.args:
        cname = request.args.get("course_name")  # enter course name
        review = Review.query.filter_by(cname=cname, pname=pname)
        return jsonify([r.serialize() for r in review])
    elif "cid" in request.args:  # enter courseID
        cid = request.args.get("cid")
        course = Course.query.filter_by(cid=cid).first()
        cname = course.name
        review = Review.query.filter_by(cname=cname, pname=pname)
        return jsonify([r.serialize() for r in review])
    else:
        review = Review.query.filter_by(pname=pname)
        return jsonify([r.serialize() for r in review])


@app.route("/getfilterscore", methods=["GET"])
def get_filterscore():
    if "desc" in request.args and request.args.get("desc") == "False":
        if 'avgscore1' in request.args:
            avgscore1 = request.args.get("avgscore1")
        else:
            avgscore1 = 5
        if 'avgscore2' in request.args:
            avgscore2 = request.args.get("avgscore2")
        else:
            avgscore2 = 5
        if 'avgscore3' in request.args:
            avgscore3 = request.args.get("avgscore3")
        else:
            avgscore3 = 5
        if "cid" in request.args:
            cid = request.args.get("cid")
            course = Course.query.filter_by(cid=cid)
            cname = course.name
        else:
            cname = request.args("cname")
        temp = Review.query.with_entities(Review.cname,Review.pname).\
            group_by(Review.cname,Review.pname).\
                having(db.and_(db.func.avg(Review.score1) <= avgscore1,
                db.func.avg(Review.score2) <= avgscore2,
                db.func.avg(Review.score3) <= avgscore3)).subquery()
        review = Review.query.filter(Review.cname==temp.c.cname,Review.pname==temp.c.pname,Review.cname==cname)
        return jsonify([r.serialize() for r in review])
    else:
        if 'avgscore1' in request.args:
            avgscore1 = request.args.get("avgscore1")
        else:
            avgscore1 = 0
        if 'avgscore2' in request.args:
            avgscore2 = request.args.get("avgscore2")
        else:
            avgscore2 = 0
        if 'avgscore3' in request.args:
            avgscore3 = request.args.get("avgscore3")
        else:
            avgscore3 = 0
        if "cid" in request.args:
            cid = request.args.get("cid")
            course = Course.query.filter_by(cid=cid).first()
            cname = course.name
        else:
            cname = request.args.get("cname")
        temp = Review.query.with_entities(Review.cname,Review.pname).\
            group_by(Review.cname,Review.pname).\
                having(db.and_(db.func.avg(Review.score1) >= avgscore1,
                db.func.avg(Review.score2) >= avgscore2,
                db.func.avg(Review.score3) >= avgscore3)).subquery()
        review = Review.query.filter(Review.cname==temp.c.cname,Review.pname==temp.c.pname,Review.cname==cname)
        return jsonify([r.serialize() for r in review])


@app.route("/getall", methods=["GET"])
def get_all():
    school = request.args.get("school")
    if "offset" in request.args:  # if user specifiy how many records to show
        offset=request.args.get("offset")
        course=Course.query.filter_by(school=school).limit(offset)
        return jsonify([c.serialize() for c in course])
    else:
        course=Course.query.filter_by(school=school).limit(15)
        return jsonify([c.serialize() for c in course])

import time
import threading
import telepot
import telegram
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop
from telegram.ext import Updater
from flask import Flask, request
import requests
import sys
import os
import logging
import json
from hashids import Hashids
hashids = Hashids()

#################################################
## response1: which method user want to use
## response2: pname/ cname/ cid             #user input          
## response3: pname/ cname/ cid            ## This will be from buttons
## response4: scores
## response5: optional things
###################################################

TOKEN = '864405474:AAGgINrELijqpInkrosYc-kAN-ImsQmVKbE'
bot = telepot.Bot(TOKEN)


PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
updater = Updater(TOKEN)
updater.deleteWebhook
updater.start_webhook(listen="0.0.0.0",port=PORT, url_path=TOKEN)
updater.bot.set_webhook("https://smt203-project-team1.herokuapp.com/{}".format(TOKEN))



mark = 0
response1 = ""
response2 = ""
getprofcourse = "http://smt203-project-team1.herokuapp.com/getprofcourse"
postReview = "http://smt203-project-team1.herokuapp.com/postreview"
getreview = "http://smt203-project-team1.herokuapp.com/getreview"
get_modreview = "http://smt203-project-team1.herokuapp.com/getmodreview"
pname = ''
cname = ''
scores = []
score1 = 0.0
score2 = 0.0
score3 = 0.0
comment = ''
advice = ''
school = ''
year = 1
mark_dic = {}
response_list = []
schools = ['SIS','SOE','SOB','SOA','SOSS','SOL']


#continuous listen
def on_chat_message(msg):
    # chat_id = msg['chat']["id"]
    try:
        response = msg["text"]
        chat_id = msg['from']['id']                                          
        global response1                                                     
        global response2
        global response3
        global mark_dic   #########store user chat_id and save the response and stage

        if chat_id not in mark_dic:
            mark = -1
            respond = {}
            mark_dic[chat_id] = [mark, respond]

        if response == '/start':
            msg = "👋 Please type / to choose /review or /search"
            validation_reply(msg, chat_id)
        elif response == '/review':#review profs
            markup = ReplyKeyboardMarkup(keyboard=[
                        [KeyboardButton(text='Post by Course ID')], [KeyboardButton(text='Post by Course Name')],
                        [KeyboardButton(text = "Post by Professor Name")],
                    ])
            bot.sendMessage(chat_id, 'Please indicate which methods would you like to use', reply_markup=markup)
            mark_dic[chat_id][0] = 0
        elif response == '/search':#search reviews
            markup = ReplyKeyboardMarkup(keyboard=[
                        [KeyboardButton(text='Search by Course ID')], [KeyboardButton(text='Search by Course Name')],
                        [KeyboardButton(text = "Search by Professor Name")],
                    ])
            bot.sendMessage(chat_id, 'Please indicate which methods would you like to use', reply_markup=markup)
            mark_dic[chat_id][0] = 0.5               
        elif response[:4] == "Post" and mark_dic[chat_id][0] == 0:#first selection of Post by what                                        
            response1 = response
            mark_dic[chat_id][1]["response1"] = response1
            step_2(response1, chat_id)
        elif response[:6] == "Search" and mark_dic[chat_id][0] == 0.5:#first selection of search by what                                        
            response1 = response
            mark_dic[chat_id][1]["response1"] = response1
            search_step_2(response1, chat_id) 
        elif mark_dic[chat_id][0] == 1:#select prof or course
            response3 = response 
            mark_dic[chat_id][1]["response3"] = response3
            step_4(response3, chat_id)
        elif mark_dic[chat_id][0] == 1.5:#get mod review by courses
            response3 = response
            mark_dic[chat_id][1]["response3"] = response3
            get_modreview(mark_dic[chat_id][1]["r"], response3, chat_id)     
        elif mark_dic[chat_id][0] == 2:#give score base on the selection
            # response4 = response
            scores = response
            mark_dic[chat_id][1]["scores"] = scores
            scoreValidation(scores,chat_id)
        elif mark_dic[chat_id][0] == 3:#give comment and finish score review
            response5 = response
            mark_dic[chat_id][1]["response5"] = response5
            step_6_1(response5, chat_id)
        elif mark_dic[chat_id][0] == 4:#ask and give advice else skip
            response6 = response
            mark_dic[chat_id][1]["response6"] = response6
            step_6_2(response6, chat_id)
        elif mark_dic[chat_id][0] == 5:
            response7 = response
            mark_dic[chat_id][1]["response7"] = response7
            step_6_3(response7, chat_id)
        elif mark_dic[chat_id][0] == 6:
            response8 = response
            mark_dic[chat_id][1]["response8"] = response8
            step_6_4(response8, chat_id)
        elif mark_dic[chat_id][1]["response1"] != "" and mark_dic[chat_id][0] == 0:    
            response2 = response
            mark_dic[chat_id][1]["response2"] = response2
            step_2_vaildation(response2, mark_dic[chat_id][1]["response1"], chat_id)
        elif mark_dic[chat_id][1]["response1"] != "" and mark_dic[chat_id][0] == 0.5:    
            response2 = response
            mark_dic[chat_id][1]["response2"] = response2
            search_step_2_vaildation(response2, mark_dic[chat_id][1]["response1"], chat_id)
        elif response == 'h' or mark_dic[chat_id][0] == 10:
            markup = ReplyKeyboardRemove()
            bot.sendMessage(chat_id, 'Hide custom keyboard', reply_markup=markup)

#######################################################################################################################################
def search_step_2(response1, chat_id):
    if response1 == "Search by Course ID":
        msg = "Please enter course code"
    elif response1 == "Search by Course Name":
        msg = "Please enter course name"
    elif response1 == "Search by Professor Name":
        msg = "Please enter professor name"
    return validation_reply(msg, chat_id)
    
def validation_reply(msg, chat_id):
    return bot.sendMessage(chat_id, msg, parse_mode=telegram.ParseMode.MARKDOWN)

def step_2(response1, chat_id):  
    if response1 == "Post by Course ID":
        msg = "Please enter course code🌑"
    elif response1 == "Post by Course Name":
        msg = "Please enter course name"
    elif response1 == "Post by Professor Name":
        msg = "Please enter professor name"
    
    return validation_reply(msg, chat_id)                              ## this step is just to check user click on which button and give corresponding respond

def search_step_2_vaildation(response2, response1, chat_id):
    global mark_dic
    if response1 == "Search by Course ID":
        if response2.isalpha() or response2.isdigit():
            mark_dic[chat_id][0] = 0.5
            msg = "Please enter the correct format of Course code"
            return validation_reply(msg, chat_id), mark_dic
        else:
            return search_step_3(response2, response1, chat_id)
    if response1 == "Search by Course Name":
        cname_without_space =response2.replace(" ", "")
        if cname_without_space.isalpha():
            return search_step_3(response2, response1, chat_id)              ## cname may not be complete and contain space
        else:
            msg = "Please enter the correct format of course name"
            return validation_reply(msg, chat_id)
    if response1 == "Search by Professor Name":
        pname_without_space = response2.replace(" ", "")
        if pname_without_space.isalpha():
            return search_step_3(response2, response1, chat_id)     ## pname contains space e.g "Tan Hwee Xian"
        else:
            msg = "Please enter the correct format of Prof name"
            return validation_reply(msg, chat_id)

# response2 = "SMT203" ## this need to get from user 
def step_2_vaildation(response2, response1, chat_id):
    if response1 == "Post by Course ID":
        if response2.isalpha() or response2.isdigit():
            msg = "Please enter the correct format of Course code"
            return validation_reply(msg, chat_id)
        else:
            return step_3(response2, response1, chat_id)
    if response1 == "Post by Course Name":
        cname_without_space =response2.replace(" ", "")
        if cname_without_space.isalpha():
            return step_3(response2, response1, chat_id)              ## cname may not be complete and contain space
        else:
            msg = "Please enter the correct format of course name"
            return validation_reply(msg, chat_id)
    if response1 == "Post by Professor Name":
        pname_without_space = response2.replace(" ", "")
        if pname_without_space.isalpha():
            return step_3(response2, response1, chat_id)     ## pname contains space e.g "Tan Hwee Xian"
        else:
            msg = "Please enter the correct format of Prof name"
            return validation_reply(msg, chat_id)

#what are the things to show in getreview...
def search_step_3(response2, response1, chat_id):
    global mark_dic
    global pname
    url = "http://smt203-project-team1.herokuapp.com/getreview"
    result = []
    review = {}
    l = []
    final = ''
    try:
        if response1 == "Search by Course ID":
            params = {"cid": response2}
            request1 = requests.get(url="http://smt203-project-team1.herokuapp.com/getprofcourse",params=params)
            if request1.status_code == 500:
                msg = "Please enter a valid course ID."
                return validation_reply(msg, chat_id)
            request = requests.get(url=url,params=params)
            if request.json() == [] or request.status_code == 500:
                msg = "No review available. Do you want to post a review?"
                validation_reply(msg, chat_id)
                msg = "/review"
                mark_dic[chat_id][0] = 0
                return validation_reply(msg, chat_id), mark_dic
            for i in request.json():
                comment = []
                advice = []
                if i["professor"] not in review:
                    if i["comment"] != None:
                        comment.append(i["comment"])
                    if i["advice"] != None:
                        advice.append(i["advice"])
                    score1 = i["score1"]
                    score2 = i["score2"]
                    score3 = i["score3"]
                    count = 1
                    review[i["professor"]] = [score1, score2, score3, count, comment, advice]
                else:
                    review[i["professor"]][0] += i["score1"]
                    review[i["professor"]][1] += i["score2"]
                    review[i["professor"]][2] += i["score3"]
                    review[i["professor"]][3] += 1
                    if i["comment"] != None:
                        review[i["professor"]][4].append(i["comment"])
                    if i["advice"] != None:
                        review[i["professor"]][5].append(i["advice"])
            for k, v in review.items():
                pname = k
                s1 = round(v[0] / v[3],2)
                s2 = round(v[1] / v[3],2)
                s3 = round(v[2] / v[3],2)
                if v[4] != []:
                    comment = v[4]
                else:
                    comment = None
                if v[5] != []:
                    advice = v[5]
                else:
                    advice = None
                re = [pname, s1, s2, s3, comment, advice]
                result.append(re)
            mark_dic[chat_id][0] = 10
            for i in result:
                final += "\n👨‍🏫 Prof *{0}* has *{1}* in clarity of teaching, *{2}* in workload and *{3}* in grading fairness.\nComments:".format(i[0], i[1], i[2], i[3])
                if i[4] == None:
                    final += "\n`None`"
                else:
                    for a in i[4]:
                        final += "\n`{0}`".format(a)
                final += "\nAdvices: "
                if i[5] == None:
                    final += "\n`None`"
                else:
                    for b in i[5]:
                        final += "\n`{0}`".format(b)
                final += "\n⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐"
            return validation_reply(final, chat_id), mark_dic
        elif response1 == "Search by Course Name":
            params = {"cname": response2}
            request1 = requests.get(url="http://smt203-project-team1.herokuapp.com/getprofcourse",params=params)
            if request1.status_code == 500:
                msg = "Please enter a valid course name."
                return validation_reply(msg, chat_id)
            request = requests.get(url=url,params=params)
            if request.json() == [] or request.status_code == 500:
                msg = "No review available. Do you want to post a review?"
                validation_reply(msg,chat_id)
                msg = "/review"
                mark_dic[chat_id][0] = 0
                return validation_reply(msg, chat_id), mark_dic
            for i in request.json():
                comment = []
                advice = []
                if i["professor"] not in review:
                    if i["comment"] != None:
                        comment.append(i["comment"])
                    if i["advice"] != None:
                        advice.append(i["advice"])
                    score1 = i["score1"]
                    score2 = i["score2"]
                    score3 = i["score3"]
                    count = 1
                    review[i["professor"]] = [score1, score2, score3, count, comment, advice]
                else:
                    review[i["professor"]][0] += i["score1"]
                    review[i["professor"]][1] += i["score2"]
                    review[i["professor"]][2] += i["score3"]
                    review[i["professor"]][3] += 1
                    if i["comment"] != None:
                        review[i["professor"]][4].append(i["comment"])
                    if i["advice"] != None:
                        review[i["professor"]][5].append(i["advice"])
            for k, v in review.items():
                pname = k
                s1 = round(v[0] / v[3],2)
                s2 = round(v[1] / v[3],2)
                s3 = round(v[2] / v[3],2)
                if v[4] != []:
                    comment = v[4]
                else:
                    comment = None
                if v[5] != []:
                    advice = v[5]
                else:
                    advice = None
                re = [pname, s1, s2, s3, comment, advice]
                result.append(re)
            mark_dic[chat_id][0] = 10
            for i in result:
                final += "\n👨‍🏫 Prof *{0}* has *{1}* in clarity of teaching, *{2}* in workload and *{3}* in grading fairness.\nComment:".format(i[0], i[1], i[2], i[3])
                if i[4] == None:
                    final += "\n`None`"  
                else: 
                    for a in i[4]:
                        final += "\n`{0}`".format(a)
                final += "\nAdvices: "
                if i[5] == None:
                    final += "\n`None`"
                else:
                    for b in i[5]:
                        final += "\n`{0}`".format(b)
                final += "\n⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐"
            return validation_reply(final, chat_id), mark_dic
        elif response1 == "Search by Professor Name":# getmodreview function
            pname = response2
            params = {"pname": response2}
            request1 = requests.get(url="http://smt203-project-team1.herokuapp.com/getprofcourse",params=params)
            if request1.status_code == 500:
                msg = "Please enter a valid Professor Name."
                return validation_reply(msg, chat_id)
            url = "http://smt203-project-team1.herokuapp.com/getmodreview"
            request = requests.get(url=url,params=params)
            if request.json() == [] or request.status_code == 500:
                msg = "No review available. Do you want to post a review?"
                validation_reply(msg,chat_id)
                msg = "/review"
                mark_dic[chat_id][0] = 0
                return validation_reply(msg, chat_id), mark_dic
            else:
                for i in request.json():
                    if i["course"] not in l:
                        l.append(i["course"])
                l.append("All")
                mark_dic[chat_id][0] = 1.5
                r = request.json()
                mark_dic[chat_id][1]["r"] = r
                mark_dic[chat_id][1]["pname"] = pname
                msg = 'Please indicate which course you want to search.'
                return send_list(l, msg, chat_id), mark_dic
    except:
        msg = "Please check your input"
        mark_dic[chat_id][0] = 0.5
        return validation_reply(msg, chat_id), mark_dic

def get_modreview(r, response3, chat_id):
    global mark_dic
    url = get_modreview
    result = []
    review = {}
    count = 0
    final = ''
    if response3 == "All":
        for i in r:
            comment =[]
            advice = []
            if i["course"] not in review:
                if i["comment"] != None:
                    comment.append(i["comment"])
                if i["advice"] != None:
                    advice.append(i["advice"])
                score1 = i["score1"]
                score2 = i["score2"]
                score3 = i["score3"]
                count = 1
                review[i["course"]] = [score1, score2, score3, count, comment, advice]
            else:
                review[i["course"]][0] += i["score1"]
                review[i["course"]][1] += i["score2"]
                review[i["course"]][2] += i["score3"]
                review[i["course"]][3] += 1
                if i["comment"] != None:
                    review[i["course"]][4].append(i["comment"])
                if i["advice"] != None:
                    review[i["course"]][5].append(i["advice"])
        for k, v in review.items():
            cname = k
            s1 = round(v[0] / v[3],2)
            s2 = round(v[1] / v[3],2)
            s3 = round(v[2] / v[3],2)
            if v[4] != []:
                comment = v[4]
            else:
                comment = None
            if v[5] != []:
                advice = v[5]
            else:
                advice = None
            re = [mark_dic[chat_id][1]["pname"], s1, s2, s3, comment, advice, cname]
            result.append(re)
        for i in result:
            final += "\n👨‍🏫 Prof *{0}* in course *{4}* has *{1}* in clarity of teaching, *{2}* in workload and *{3}* in grading fairness. \nComments:".format(i[0], i[1], i[2], i[3],i[6])
            if i[4] == None:
                final += "\n`None`"
            else:
                for a in i[4]:
                    final += "\n`{0}`".format(a)
            final += "\nAdvices: "
            if i[5] == None:
                final += "\n`None`"
            else:
                for b in i[5]:
                    final += "\n`{0}`".format(b)
            final += "\n⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐"
        return validation_reply(final, chat_id), mark_dic
    else:
        cname = response3
        for i in r:
            comment =[]
            advice = []
            if i["course"] == cname:
                if i["course"] not in review:
                    if i["comment"] != None:
                        comment.append(i["comment"])
                    if i["advice"] != None:
                        advice.append(i["advice"])
                    score1 = i["score1"]
                    score2 = i["score2"]
                    score3 = i["score3"]
                    count = 1
                    review[i["course"]] = [score1, score2, score3, count, comment, advice]
                else:
                    review[i["course"]][0] += i["score1"]
                    review[i["course"]][1] += i["score2"]
                    review[i["course"]][2] += i["score3"]
                    review[i["course"]][3] += 1
                    if i["comment"] != None:
                        review[i["course"]][4].append(i["comment"])
                    if i["advice"] != None:
                        review[i["course"]][5].append(i["advice"])
        for k, v in review.items():
            cname = k
            s1 = round(v[0] / v[3],2)
            s2 = round(v[1] / v[3],2)
            s3 = round(v[2] / v[3],2)
            if v[4] != []:
                comment = v[4]
            else:
                comment = None
            if v[5] != []:
                advice = v[5]
            else:
                advice = None
            re = [mark_dic[chat_id][1]["pname"], s1, s2, s3, comment, advice, cname]
            result.append(re)
        for i in result:
            final += "\n👨‍🏫 Prof *{0}* in course *{4}* has *{1}* in clarity of teaching, *{2}* in workload and *{3}* in grading fairness. \nComments:".format(i[0], i[1], i[2], i[3],i[6])
            if i[4] == None:
                final += "\n`None`"
            else:
                for a in i[4]:
                    final += "\n`{0}`".format(a)
            final += "\nAdvices: "
            if i[5] == None:
                final += "\n`None`"
            else:
                for b in i[5]:
                    final += "\n`{0}`".format(b)
            final += "\n⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐"
        return validation_reply(final, chat_id), mark_dic
##############################################################################################
#call api append result to l
def step_3(response2, response1, chat_id):  ## vaildate the input and start calling API          
    global mark_dic
    global cname
    global response_list
    l = []
    url = getprofcourse
    try:
        if response1 == "Post by Course ID": 
            params = {"cid": response2}
            request = requests.get(url=url,params=params)
            if request.status_code == 500 or request.json() == {}:
                msg = "Please enter a valid Course ID"
                return validation_reply(msg, chat_id)
            else:
                for i in request.json():
                    l.append(i["professor"])
                    cname = i["course"]
        elif response1 == "Post by Course Name":
            params = {"cname": response2}
            cname = response2
            request = requests.get(url=url,params=params)
            if request.status_code == 500 or request.json() == {}:
                msg = "Please enter a valid Course Name."
                return validation_reply(msg, chat_id)
            else:
                for i in request.json():
                    l.append(i["professor"])
        elif response1 == "Post by Professor Name":
            params = {"pname": response2}
            pname = response2
            request = requests.get(url=url,params=params)
            if request.json() == {} or request.status_code == 500:
                msg = "Please enter a valid prof name"
                return validation_reply(msg, chat_id)
            else:
                for i in request.json():
                    l.append(i["course"])
        response_list = l
        mark_dic[chat_id][0] = 1
        mark_dic[chat_id][1]["cname"] = cname
        mark_dic[chat_id][1]["response_list"] = response_list
        msg = 'Please indicate which professor/course you want to review.🌘'
        return send_list(l, msg, chat_id), mark_dic
    except:
        msg = "Please check your input"
        mark_dic[chat_id][0] = 0
        return validation_reply(msg, chat_id), mark_dic
#############################################################################################################
#prof buttons or couse name
def send_list(l, msg, chat_id):
    keyboard = []
    for i in l:
        z = []
        x = i
        z.append(x)
        keyboard.append(z)
    markup = ReplyKeyboardMarkup(keyboard=keyboard)
    return bot.sendMessage(chat_id, msg, reply_markup=markup,parse_mode=telegram.ParseMode.MARKDOWN)

# response3 = "xxx"      ## base on which button user select
#score
def step_4(response3, chat_id):
    global mark_dic

    if response3 not in response_list:
        mark_dic[chat_id][0] = 1
        msg = "Please check your input."
        return validation_reply(msg, chat_id), mark_dic
    if mark_dic[chat_id][1]["response1"] == "Post by Course ID":
        mark_dic[chat_id][1]["pname"] = response3
    elif mark_dic[chat_id][1]["response1"] == "Post by Course Name":
        mark_dic[chat_id][1]["pname"] = response3
    elif mark_dic[chat_id][1]["response1"] == "Post by Professor Name":
        mark_dic[chat_id][1]["cname"] = response3
    review_scores = """
    Please provide scores between 0 to 5 based on
    - *Clarity of Teaching*
    - *Workload*
    - *Grading Fairness*
    For example:
    Clarity of Teching has 3.5. Workload has 4. And Grading has 5.
    Just enter: *3.5,4,5* 🌗"""
    mark_dic[chat_id][0] = 2
    return bot.sendMessage(chat_id, review_scores, parse_mode=telegram.ParseMode.MARKDOWN), mark_dic

#convert to button
def step_5(chat_id): 
    global mark_dic
    mark_dic[chat_id][0] = 3
    #return bot.sendMessage(chat_id, review_qns), mark
    msg = "Following questions are optional. Please simply provide the information or press 'Skip' to skip the question."
    l = ["Skip further comment"]
    msg = "Please enter further comment for the prof or course if any.🌖"
    return send_list(l, msg, chat_id), mark_dic

def step_6_1(response5, chat_id):
    global mark_dic
    global comment
    l = ["Skip for advice"]
    msg = "Please enter your advice for prof to improve if any.🌕"
    try:
        if response5 == "Skip further comment":
            comment = None
            mark_dic[chat_id][0] = 4
            mark_dic[chat_id][1]["comment"] = comment
            return send_list(l, msg, chat_id),mark_dic
        else:
            comment = response5
            mark_dic[chat_id][0] = 4
            mark_dic[chat_id][1]["comment"] = comment
            return send_list(l, msg, chat_id), mark_dic
    except:
        msg = response5
        mark_dic[chat_id][0] = 3
        return validation_reply(msg, chat_id), mark_dic

def step_6_2(response6, chat_id):
    global mark_dic
    global advice
    l = ["Skip entering school"]
    msg = "Please enter your school. E.g. *SIS*🌝"
    try:
        if response6 == "Skip for advice" or response6 == "Skip further comment":
            advice = None
            mark_dic[chat_id][0] = 5
            mark_dic[chat_id][1]["advice"] = advice
            return send_list(l, msg, chat_id),mark_dic
        else:
            advice = response6
            mark_dic[chat_id][0] = 5
            mark_dic[chat_id][1]["advice"] = advice
            return send_list(l, msg, chat_id),mark_dic
    except:
        msg = response6
        mark_dic[chat_id][0] = 4
        return validation_reply(msg, chat_id), mark_dic

def step_6_3(response7, chat_id):
    global mark_dic
    global school
    l = ["Skip entering current year."]
    msg = "Please enter your current year in integer. E.g. *3* ☀️"
    try:
        if response7 == "Skip entering school":
            school = None
            mark_dic[chat_id][0] = 6
            mark_dic[chat_id][1]["school"] = school
            return send_list(l, msg, chat_id),mark_dic
        else:
            school = response7
            if school in schools:
                mark_dic[chat_id][0] = 6
                mark_dic[chat_id][1]["school"] = school
                return send_list(l, msg, chat_id),mark_dic
            else:
                mark_dic[chat_id][0] = 5
                msg = "Please enter your school. E.g. *SIS,SOE,SOB,SOA,SOSS*"
                return validation_reply(msg, chat_id), mark_dic
    except:
        msg = response7
        mark_dic[chat_id][0] = 5
        return validation_reply(msg, chat_id), mark_dic

def step_6_4(response8, chat_id):
    global mark_dic
    global year
    msg = "That's all for the review. Thank you.🦁🦁🦁"
    try:
        if response8 == "Skip entering current year.":
            year = None
            mark_dic[chat_id][0] = 10
            mark_dic[chat_id][1]["year"] = year
            postReview(chat_id, mark_dic)
            return validation_reply(msg, chat_id), mark_dic
        else:
            try:
                year = int(response8)
            except:
                msg = "Please enter a integer"
                mark_dic[chat_id][0] = 6
                return validation_reply(msg, chat_id), mark_dic
            if(year < 1 or year > 4):
                msg = "Please enter a integer between 1 to 4"
                mark_dic[chat_id][0] = 6
                return validation_reply(msg, chat_id), mark_dic
            else:
                mark_dic[chat_id][0] = 10
                mark_dic[chat_id][1]["year"] = year
                postReview(chat_id, mark_dic)
                #check_chat_id(chat_id)
                return validation_reply(msg, chat_id), mark_dic
    except:
        msg = "Something went wrong..."
        mark_dic[chat_id][0] = 6
        return validation_reply(msg, chat_id), mark_dic

#check score input within 0 to 5
def scoreValidation(scores,chat_id):
    global mark_dic
    global score1
    global score2
    global score3
    try:
        scores = scores.split(',')
        score1 = float(scores[0])
        score2 = float(scores[1])
        score3 = float(scores[2])
    except:
        msg = "Please provide three scores."
        return validation_reply(msg, chat_id), mark_dic
    if(score1<0 or score2<0 or score3<0):
        msg = "Score could not be less than 0. Please enter your score again."
        mark_dic[chat_id][0] = 2
        return validation_reply(msg, chat_id), mark
    elif(score1>5 or score2>5 or score3>5):
        msg = "Score could not be larger than 5. Please enter your score again."
        mark_dic[chat_id][0] = 2
        return validation_reply(msg, chat_id), mark
    else:
        mark_dic[chat_id][0] = 3
        msg = "Thank you for your score review"
        validation_reply(msg, chat_id)
        mark_dic[chat_id][1]["score1"] = score1
        mark_dic[chat_id][1]["score2"] = score2
        mark_dic[chat_id][1]["score3"] = score3
        return step_5(chat_id), mark_dic

#post review function
#, pname, cname, score1, score2, score3, comment, advice, school, year
def postReview(chat_id, mark_dic):
    hashid = hashids.encode(chat_id)
    #nhashid = hashids.decode(hashid) #decode
    pname = mark_dic[chat_id][1]["pname"]
    cname = mark_dic[chat_id][1]["cname"]
    score1 = mark_dic[chat_id][1]["score1"]
    score2 = mark_dic[chat_id][1]["score2"]
    score3 = mark_dic[chat_id][1]["score3"]
    comment = mark_dic[chat_id][1]["comment"]
    advice = mark_dic[chat_id][1]["advice"]
    school = mark_dic[chat_id][1]["school"]
    year = mark_dic[chat_id][1]["year"]
    json = {"reviewer": hashid, "pname":pname, "cname":cname, "score1":score1, "score2":score2, "score3":score3, "comment":comment, "advice":advice, "school":school, "year":year}
    postReview = "http://smt203-project-team1.herokuapp.com/postreview"
    mark_dic[chat_id][0] = 10
    if comment == None:
        comment = "No comment."
    if advice == None:
        advice = "No advice"
    msg = """👨‍🏫 Prof *{0}* in *{1}* got scores *{2}* for Clarity *{3}* for Workload *{4}* for Grading with comment: *{5}* and advice: *{6}*. 
You are in year *{8}* from *{7}* .\n⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐""".format(pname,cname,score1, score2, score3, comment, advice, school, year)
    request = requests.post(url=postReview,json=json)
    if school==None or year == None:
        msg = """👨‍🏫 Prof *{0}* in *{1}* got scores *{2}* for Clarity *{3}* for Workload *{4}* for Grading with comment: *{5}* and advice: *{6}*.\n⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐""".format(pname,cname,score1, score2, score3, comment, advice)
    validation_reply(msg, chat_id)
    if request.status_code == 200:
        msg = "Your review has been posted sucessfully."
        return validation_reply(msg, chat_id), mark_dic #return status
    else:
        msg = "Posting failed. You have posted the review for the prof and course."
        return validation_reply(msg, chat_id), mark_dic #return status


###################################################################################################################################
#bot = telepot.Bot("830250985:AAFeA-dy4mB1kXZbK_kBc6pBeT5xD7sqPu0")
#bot = telepot.Bot("864405474:AAGgINrELijqpInkrosYc-kAN-ImsQmVKbE")

@app.route("/"+TOKEN,methods=['POST'])
def get_updates():
    on_chat_message(request.json)
    return 200


if __name__ == '__main__':
    updater = Updater(TOKEN)
    run(updater)







# your code ends here
if __name__ == "__main__":
    app.run(debug=True)
