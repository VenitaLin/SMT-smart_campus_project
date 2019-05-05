import time
import threading
import telepot
import telegram
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop
import requests
from hashids import Hashids
hashids = Hashids()
## Current Problem faced:
## 1. I have declared the global variables (mark) but when I update them in the later on functions, it does not change...
## 2. line 38 will the the chat_id but I have to pass it as a parameter to other functions instead of letting it become a global variable.
## 3. Because it is very hard to differentiate what the user inputs so we didn't do much vaildation and assuming user can follow the correct format all the way.
## 4. If the user input part of the Prof name/ course name, our API will Post for them and return the possible output for them to choose. But because of problem 3, 
##    it is very hard to achieve this function
## p.s. We have link this bot to our api so from line 113-129 will be hard code for now.

#################################################
## response1: which method user want to use
## response2: pname/ cname/ cid             #user input          
## response3: pname/ cname/ cid            ## This will be from buttons
## response4: scores
## response5: optional things
###################################################
"""
$ python3.5 skeleton_route.py <token>
It demonstrates:
- passing a routing table to `message_loop()` to filter flavors.
- the use of custom keyboard and inline keyboard, and their various buttons.
Remember to `/setinline` and `/setinlinefeedback` to enable inline mode for your bot.
It works like this:
- First, you send it one of these 4 characters - `c`, `h` - and it replies accordingly:
    - `c` - a custom keyboard with various buttons
    - `h` - hide custom keyboard
- Press various buttons to see their effects
"""
mark = 0
response1 = ""
response2 = ""
getprofcourse = "http://smt203-project-team1.herokuapp.com/getprofcourse"
postReview = "http://smt203-project-team1.herokuapp.com/postreview"
getreview = "http://smt203-project-team1.herokuapp.com/getreview"
get_modreview = "http://smt203-project-team1.herokuapp.com/getmodreview"
#get_all = "http://smt203-project-team1.herokuapp.com/getall"
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
# chat_id = "386055474" ## this need to extract from database

#continuous listen
def on_chat_message(msg):
    # chat_id = msg['chat']["id"]
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat:', content_type, chat_type, chat_id)                                                                 
    if content_type != 'text':                                            
        return                                                     
    global response1                                                     
    global response2
    global response3
    global mark_dic   #########store user chat_id and save the response and stage
    response = msg['text']

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
        mark_dic[chat_id][1]={}
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
            if request.status_code == 500 or request.json() == []:
                msg = "Please enter a valid Course ID"
                return validation_reply(msg, chat_id)
            else:
                for i in request.json():
                    l.append(i["professor"])
                    cname = i["course"]
                mark_dic[chat_id][0] = 1
                mark_dic[chat_id][1]["cname"] = cname
        elif response1 == "Post by Course Name":
            params = {"cname": response2}
            cname = response2
            request = requests.get(url=url,params=params)
            if request.status_code == 500 or request.json() == []:
                msg = "Please enter a valid Course Name."
                return validation_reply(msg, chat_id)
            else:
                for i in request.json():
                    l.append(i["professor"])
                mark_dic[chat_id][0] = 1
                mark_dic[chat_id][1]["cname"] = cname
        elif response1 == "Post by Professor Name":
            params = {"pname": response2}
            pname = response2
            request = requests.get(url=url,params=params)
            if request.json() == [] or request.status_code == 500:
                msg = "Please enter a valid prof name"
                return validation_reply(msg, chat_id)
            else:
                for i in request.json():
                    l.append(i["course"])
                mark_dic[chat_id][0] = 1
                mark_dic[chat_id][1]["pname"] = response2
                response_list = l
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
    if mark_dic[chat_id][1]["response1"] == "Post by Course ID":
        mark_dic[chat_id][1]["pname"] = response3
    elif mark_dic[chat_id][1]["response1"] == "Post by Course Name":
        mark_dic[chat_id][1]["pname"] = response3
    elif mark_dic[chat_id][1]["response1"] == "Post by Professor Name":
        mark_dic[chat_id][1]["cname"] = response3
        if response3 not in response_list:
            mark_dic[chat_id][0] = 1
            msg = "Please check your input."
            return validation_reply(msg, chat_id), mark_dic
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
            mark_dic[chat_id][1]["year"] = None
            postReview(chat_id, mark_dic)
            mark_dic[chat_id][0] = 10
            return validation_reply(msg, chat_id), mark_dic
        else:
            try:
                year = int(response8)
            except:
                msg = "Please enter a integer"
                mark_dic[chat_id][0] = 6
                return validation_reply(msg, chat_id), mark_dic
            if(year < 1 or year > 5):
                msg = "Please enter a integer between 1 to 4"
                mark_dic[chat_id][0] = 6
                return validation_reply(msg, chat_id), mark_dic
            else:
                mark_dic[chat_id][1]["year"] = year
                postReview(chat_id, mark_dic)
                mark_dic[chat_id][0] = 10
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
bot = telepot.Bot("864405474:AAGgINrELijqpInkrosYc-kAN-ImsQmVKbE")
# bot = telepot.Bot("711112176:AAEfZ1a1l26xXUlnpFEm3D7t5C4W0SHfzQU")
MessageLoop(bot, on_chat_message).run_as_thread()
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(5)