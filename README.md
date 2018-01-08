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

# development environment
> python - 3.6.3
> mongo - 2.6.12
> django - 1.11.7
> MongoDB shell version - 2.6.12
> pymongo - 3.5.1
> Operating system - Red Hat Enterprise Linux 7
> anaconda 3
> pycharm - 2017.2.4



