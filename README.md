# telecommunication

yi@XPS:~/jyvaskyla/telecommunication$ python manage.py runserver


## Create a new mongo user
db.createUser({user:"**", pwd:"******", roles:[{role:"userAdminAnyDatabase", db:"admin"}]})

## create a new database
use newDatabase

## import data into mongo database
mongoimport --db 5gopt --collection normal --type csv --file ~/code/data/normal_800m.csv --headerline --ignoreBlanks
mongoimport --db 5gopt --collection main_file_with_UserTHR --type csv --file ~/Downloads/main_file_with_UserTHR.csv --fields "Time, LocationX, LocationY, UserID, CellID, RSRP, RSRQ, SINR, UserThR" --ignoreBlanks

## install mongo c driver and mongo cxx driver to implment communication between ns-allinone-3.26 and mongo v2.6.12
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local -DCMAKE_PREFIX_PATH=/usr/local ..

## restore bson file into mongodb
mongorestore -d db_name -c collection_name path/file.bson
* ./mongorestore -d 5gopt -c normal /home/tupevarj/Downloads/normal.bson
* ./mongorestore -d 5gopt -c controlpanel /home/tupevarj/Downloads/controlpanel.bson
* ./mongorestore -d 5gopt -c outage /home/tupevarj/Downloads/outage.bson
* ./mongorestore -d 5gopt -c event_log /home/tupevarj/Downloads/event_log.bson
* ./mongorestore -d 5gopt -c main_file_with_UserTHR /home/tupevarj/Downloads/main_file_with_UserTHR.bson

# development environment
* python - 3.6.3
* mongo - 2.6.12
* django - 1.11.7
[pip install Django==1.11.7]
* MongoDB shell version - 2.6.12
* pymongo - 3.5.1
[pip install pymongo==3.1.1]
* Operating system - Red Hat Enterprise Linux 7
* anaconda 3
https://anaconda.org/anaconda/python/files

* pycharm - 2017.2.4

# related documentation for this project
* MongoDB C Driver 1.9.0 [http://mongoc.org/libmongoc/current/index.html]
* MongoDB C++ Driver manual [https://mongodb.github.io/mongo-cxx-driver/]
* PyMongo 3.6.0 Documentation [https://api.mongodb.com/python/current/]
* MongoEngine Documentation [http://docs.mongoengine.org/]

# Match between display figures in front end and database

| Display in Front End          | Data in MongoDB                     |
| ----------------------------- | ----------------------------------- |
| unnormal cell detection table | Fake data in Backend not from Mongo |
| Domination Map                | dominationmap                       |
| throughput line graph         | main_file_with_UserTHR              |

Collection schemas

| dominationmap |   x   |   y   |   z   |  sinr  |
| ------------- | ----- | ----- | ----- | ------ |
|     Demo      | -250  | -250  | 1.5   |  1.45  |

| main_file_with_UserTHR | Time | UserThR | LocationX | UserID | CellID | RSRP | RSRQ | SINR | LocationY |
| ---------------------- | ---- | ------- | --------- | ------ | ------ | ---- | ---- | ---- | --------- |
| Demo                   | 0.2  | NaN     |   948     |  1     | 1      | -113 | NaN  |  NaN |  1429     |





 

# to do list
1.  set up Apache when it's ready to deploy Django in production.
