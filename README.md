# telecommunication

yi@XPS:~/jyvaskyla/telecommunication$ python manage.py runserver


## Create a new mongo user
db.createUser({user:"**", pwd:"******", roles:[{role:"userAdminAnyDatabase", db:"admin"}]})

## create a new database
use newDatabase

## import data into mongo database
mongoimport --db 5gopt --collection normal --type csv --file ~/code/data/normal_800m.csv --headerline --ignoreBlanks
mongoimport --db 5gopt --collection main_file_with_UserTHR --type csv --file ~/Downloads/main_file_with_UserTHR.csv --fields "Time, LocationX, LocationY, UserID, CellID, RSRP, RSRQ, SINR, UserThR" --ignoreBlanks

