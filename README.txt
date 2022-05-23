1.Install and extract the added zip file

2.Open a terminal and get to the path of the 'basicmatcherproject' folder you just extracted

3.Type "pip install django",to install django

4.Type "pip install mysqlclient",to install mySql tools

5.Go to the folder you just extracted and in that folder go to basicmatcherproject

6.right click settings.py and open the file using Notepad

7.Go to line 77 and update the login information of your database

8.Open a terminal and get to the path of the 'basicmatcherproject' folder you just extracted

9.Type "python manage.py runserver" to run the server on your local host

10.Open an internet browser and insert 'http://127.0.0.1:8000/admin/' in the url line
Username='admin'
password='admin'

11.Insert skills,jobs and candidate to the database

12.Type 'http://127.0.0.1:8000' in the url line of your browser

13.Type a Job title in the textbox and press submit

____________SQL Tables______________


CREATE TABLE Candidate (
    id int NOT NULL AUTO_INCREMENT,
    Title varchar(100),
    skills varchar(100),
    PRIMARY KEY (id)
);

CREATE TABLE Job ( 
    Title varchar(100), 
    skills varchar(100),
    PRIMARY KEY (Title) );

CREATE TABLE Skill (
    name varchar(100),
    PRIMARY KEY (name)
);

CREATE TABLE candidate_skill (
    candidate_id int,
    skill varchar(100),
    exist boolean,
    PRIMARY KEY (Candidate_id,skill),
    foreign key (candidate_id) references candidate(id),
    foreign key (skill) references skill(name)
);

CREATE TABLE job_skill (
    job_title varchar(100),
    skill varchar(100),
    exist boolean,
    PRIMARY KEY (job_title,skill),
    foreign key (job_title) references job(title),
    foreign key (skill) references skill(name)
);

