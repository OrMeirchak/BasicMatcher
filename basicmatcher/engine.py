from gettext import Catalog
from pickle import TRUE
from xmlrpc.client import boolean
from basicmatcher.models import *
import re
from django.db import connection

class jobTitleDoesntExist(Exception):
    pass

#The function returns the index of the best candidate
def matcherEngine(jobTitle:str)->int:
    fullTitleMatchList=fullTitleMatch(jobTitle)
    if(len(fullTitleMatchList)==1):
        return fullTitleMatchList[0][0]
    else:
       updateCandidateSkill()
       updateJobSkill(jobTitle)
       
       if(len(fullTitleMatchList)>1):
          skillMatchesList=getSkillMatches(jobTitle,True)
          return skillMatchesList[0][0]
       else:#There is no candidate with matching skills
         skillMatchesList=getSkillMatches(jobTitle,False)
       
         if(len(skillMatchesList)==1):
           return skillMatchesList[0][0]
         
         if(len(skillMatchesList)>1):
           partialTitleMatchList= partialTitleMatch(jobTitle,skillMatchesList) 
           if partialTitleMatchList is None:
               return skillMatchesList[0][0]
           else:
            return partialTitleMatchList[0]  
         else:#There is no candidate with matching skills or title
           partialTitleMatchList=  partialTitleMatch(jobTitle,None)
           if partialTitleMatchList is None:
               return None
           else:
            return partialTitleMatchList[0]

#The method returns a list of candidates whose title is the same as the job title By using a SQL query      
def fullTitleMatch(jobTitle:str)->list:
    cursor=connection.cursor()
    cursor.execute('''SELECT * FROM candidate where title = "{}"'''.format(jobTitle))
    return list(cursor.fetchall())


#The method creates a view of the candidates who have the relevant skills for the job
#and returns a list of candidates with maximum skill matching amount
#In case of fullTitleMatch=True : The method return only candidates whose title is the same as the job title 
def getSkillMatches(jobTitle:str,fullTitleMatch:bool)->list:
    cursor=connection.cursor()
    if(fullTitleMatch is False):
       cursor.execute(
'''CREATE VIEW countMatches AS
select candidate.title as title,candidate.id as id,count(*) as counter
from job_skill,candidate_skill,candidate
where candidate_skill.skill=job_skill.skill
and candidate_skill.exist=1
and candidate_id=candidate.id
and job_skill.exist=1
and job_title="{}"
group by candidate_id
'''.format(jobTitle)
           )
    else:
              cursor.execute(
'''CREATE VIEW countMatches AS
select candidate.title as title,candidate.id as id,count(*) as counter
from job_skill,candidate_skill,candidate
where candidate_skill.skill=job_skill.skill
and candidate_skill.exist=1
and job_skill.exist=1
and candidate_id=candidate.id
and job_title="{}"
and candidate.title=job_title
and candidate.id=candidate_id
group by candidate_id
'''.format(jobTitle)
           )

    cursor.execute(
'''SELECT id,title, counter
FROM countmatches
WHERE counter = (SELECT MAX(counter) FROM countmatches);
'''
           )

    res=cursor.fetchall()
    if cursor:
        cursor.execute('''drop view countmatches''')
        return list(res)
    else:
        cursor.execute('''drop view countmatches''')
        return []


#The method recieves a job title and returns the first candidate whose title has a word that also appears in the title of the job.
#If the method recieves a list of candidates it will only check the input list
#Else the method will check for each entity in the job table
def partialTitleMatch(jobTitle:str,candidateList:list):
    if(candidateList is None):
       cursor=connection.cursor()
       cursor.execute(
'''select *
from candidate
'''
           )
       candidateList=cursor.fetchall()
    
    for candidate in candidateList:
        if checkPartialMatch(candidate[1],jobTitle):
            return candidate
    return None


#The method get a job title and for each skill from the skill table updates whether it exists in the job description or not
#In case there is no job in the job table with the input title the method will throw an jobTitleDoesntExist exception
def updateJobSkill(jobTitle:str):
    cursor=connection.cursor()
    cursor.execute('''SELECT * FROM job where title = "{}"'''.format(jobTitle))
    jobEntity=cursor.fetchone()
    if (jobEntity is None):
        raise jobTitleDoesntExist
    else: 
        for skillEntity in Skill.objects.all():
            updateJobSkillEntity(jobEntity,skillEntity)
        
#The method get a job entity and a skill entity and checks if the skill appears in the job entity and inserts them to job_skill table
def updateJobSkillEntity(jobEntity,skillEntity):
    if re.search(re.escape(skillEntity.name), re.escape(jobEntity[1]),re.IGNORECASE):
        JobSkill.objects.get_or_create(job_title=Job(title=jobEntity[0],skills=jobEntity[1]),skill=skillEntity,exist=1)
    else:
        JobSkill.objects.get_or_create(job_title=Job(title=jobEntity[0],skills=jobEntity[1]),skill=skillEntity,exist=0)  

#For each new skill that does not exist in the candidate_skill table the method will check which candidates have the requiered skill and inserts it to the candidate_skill table
#For any candidate who does not exist in the candidate_skill table the method will check for each skill in the skill table whether it exists for the candidate and insert it to the candidate_skill table
def updateCandidateSkill():  
   skillsNotUpdated=getSkillsNotUpdated()
   skillsList=getSkillsList()
   candidatesNotUpdated=getCandidatesNotUpdated()
   candidatesUpdated=getCandidatesUpdated()

   for candidateEntity in candidatesUpdated:
        for skillEntity in skillsNotUpdated:
            updateCandidateSkillEntity(candidateEntity,skillEntity)

   for candidateEntity in candidatesNotUpdated:
        for skillEntity in skillsList:
            updateCandidateSkillEntity(candidateEntity,skillEntity)


#The method returns a list of skills that exist in the skill table and doesn't exist in the skill_candidate table
def getSkillsNotUpdated():
    cursor=connection.cursor()
    cursor.execute('''SELECT * FROM skill where not exists (select * from candidate_skill where candidate_skill.skill = skill.name) ''')
    if cursor:
        return cursor.fetchall()
    else:
        return []


#The method returns the list of skills that exist in the skill table
def getSkillsList():
    cursor=connection.cursor()
    cursor.execute('''SELECT * FROM skill''')
    if cursor:
        return cursor.fetchall()
    else:
        return []


#The method returns a list of candidates that exists in the candidate table and doesn't exist in the candidate_skill table
def getCandidatesNotUpdated():       
    cursor=connection.cursor()
    cursor.execute('''SELECT * FROM candidate where not exists (select * from candidate_skill where candidate_skill.candidate_id = candidate.id) ''')
    if cursor:
       return cursor.fetchall()
    else:
       return []


#The method returns a list of candidates that exists in the skills table and also in the candidate_skills table
def getCandidatesUpdated():
    cursor=connection.cursor()
    cursor.execute('''SELECT * FROM candidate where exists (select * from candidate_skill where candidate_skill.candidate_id = candidate.id) ''')
    if cursor:
       return cursor.fetchall()
    else:
        return []


 #The method get a candidate entity and a skill entity and checks if the skill appears in the job entity and adds it to candidate_skill table
def updateCandidateSkillEntity(candidateEntity,skillEntity):
    if re.search(re.escape(skillEntity[0]), re.escape(candidateEntity[2]),re.IGNORECASE):
        CandidateSkill.objects.get_or_create(candidate_id=candidateEntity[0],skill=Skill(name=skillEntity[0]),exist=1)
    else:
        CandidateSkill.objects.get_or_create(candidate_id=candidateEntity[0],skill=Skill(name=skillEntity[0]),exist=0)  


#The method return 1 if s0 Contains s1 in
def checkPartialMatch(s0:str,s1:str):
    s0 = s0.lower()
    s1 = s1.lower()
    s0List = s0.split(" ")
    s1List = s1.split(" ")
    return len(list(set(s0List)&set(s1List)))


    

