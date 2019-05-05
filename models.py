from app import db

class Course(db.Model):
    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(80), nullable=False, unique=True)
    school = db.Column(db.String(10), nullable=False)
    prof_course = db.relationship(
        'Prof_Course', back_populates='course', cascade='all', lazy=True, uselist=True)

    def __init__(self, cid, name, school, prof_course=None):
        self.cid = cid
        self.name = name
        self.school = school
        prof_course = [] if prof_course is None else prof_course
        self.prof_course = prof_course
    
    def serialize(self):
        return{
            'id' : self.id,
            'course id' : self.cid,
            'name' : self.name,
            'school' : self.school
        }


class Professor(db.Model):
    __tablename__ = "professor"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    prof_course = db.relationship(
        'Prof_Course', back_populates='professor', cascade='all', lazy=True, uselist=True)

    def __init__(self, name, prof_course=None):
        self.name = name
        prof_course = [] if prof_course is None else prof_course
        self.prof_course = prof_course

    def serialize(self):
        return{
            'id' : self.id,
            'name' : self.name
        }


class Prof_Course(db.Model):
    __tablename__ = "prof_course"
    cname = db.Column(db.String(80), db.ForeignKey('course.name'))
    pname = db.Column(db.String(80), db.ForeignKey('professor.name'))
    professor = db.relationship('Professor', back_populates='prof_course')
    course = db.relationship('Course', back_populates='prof_course')
    review = db.relationship('Review', back_populates='prof_course', cascade='all', lazy=True, uselist=True)
    __table_args__ = (db.PrimaryKeyConstraint(
        'cname', 'pname', name='prof_course_pk'), {})

    def __init__(self, cname, pname, review=None):
        self.cname = cname
        self.pname = pname
        review = [] if review is None else review
        self.review = review

    def serialize(self):
        return{
            'course' : self.cname,
            'professor' : self.pname
        }


class Review(db.Model):
    __tablename__ = "review"
    reviewer = db.Column(db.String(80), primary_key=True)
    pname = db.Column(db.String(80), primary_key=True)
    cname = db.Column(db.String(80), primary_key=True)
    score1 = db.Column(db.Float, nullable=False)
    score2 = db.Column(db.Float, nullable=False)
    score3 = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=True)
    school = db.Column(db.String(10), nullable=True)
    comment = db.Column(db.String(300), nullable=True)
    advice = db.Column(db.String(300), nullable=True)
    __table_args__ = (db.ForeignKeyConstraint(['pname', 'cname'], ['prof_course.pname', 'prof_course.cname']),)
    prof_course = db.relationship('Prof_Course', back_populates='review')

    def __init__(self, reviewer, pname, cname, score1, score2, score3, year=None, school=None, comment=None, advice=None):
        self.reviewer = reviewer
        self.pname = pname
        self.cname = cname
        self.score1 = score1
        self.score2 = score2
        self.score3 = score3
        self.school = school
        self.year = year
        self.comment = comment
        self.advice = advice

    def serialize(self):
        return{
            'professor' : self.pname,
            'course' : self.cname,
            'score1' : self.score1,
            'score2' : self.score2,
            'score3' : self.score3,
            'year' : self.year,
            'school': self.school,
            'comment' : self.comment,
            'advice' : self.advice
        }
