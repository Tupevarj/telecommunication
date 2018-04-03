import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc


dataset = pd.read_csv("/home/tupevarj/Projects/MachineLearning/training.csv")


# Converting RSRP and RSRQ values into floats
array_x = []   #####
array_y = []

#print (array_x.shape)

i_max = len(dataset)
training_data_x = list()
print (i_max)
for i in range(0, i_max):
    row = []
    row2 = []
    skip = False
    dataset_row = dataset.iloc[i]
    for j in range(0, 12):
        value = float(dataset_row[j])
        if not np.isnan(value):
            row.append(float(dataset_row[j]))
            if j > 3:
                row2.append(float(dataset_row[j]))
        else:
            skip = True
    if not skip:
        array_x.append(row)
        training_data_x.append(row2)
        if dataset_row[12] == 0:
            array_y.append(False)
        else:
            array_y.append(True)


# splitting of data
X_train, X_test, y_train, y_test= train_test_split(array_x,array_y,test_size = 0.3, random_state=0)
XX_train=[]
XX_test=[]
for i in range(0,len(X_test)):
    row = []
    for col in range(2, 10):
        row.append(X_test[i][col])
    XX_test.append(row)
#print (array_x)
#Fitting random forest regression to the dataset


for i in range(0,len(X_train)):
    row = []
    for col in range(4, 12):
        row.append(X_train[i][col])
    XX_train.append(row)

from sklearn.ensemble import RandomForestRegressor
regressor= RandomForestRegressor(n_estimators=10, random_state=0)

regressor.fit(XX_train,y_train)


y_pred = regressor.predict(np.asarray(XX_test))

#print("y_pred")

#print (y_pred)

actual = y_test
predictions = y_pred

# print (predictions)
#
false_positive_rate, true_positive_rate, thresholds = roc_curve(actual, predictions)
#
# roc_auc = auc(false_positive_rate, true_positive_rate)
# print ("roc_auc")
# print (roc_auc)
#
# fig = plt.figure()
# # #plt.plot( X_train,y_pred, color='blue')
# plt.plot( false_positive_rate,true_positive_rate, color='blue')
# plt.title("Abnormal Users Detection Performance")
# plt.xlabel("FPR")
# plt.ylabel("TPR")
# plt.show()
#print ("Score:", regressor.score(X_test, y_test))
# #fig.savefig('plt_random_forest_regressio_9col.png')



# Dump the trained decision tree classifier with Pickle
random_forest_pkl_filename = 'random_forest_classifier_20170212.pkl'
# Open the file to save as pkl file
random_forest_model_pkl = open(random_forest_pkl_filename, 'wb')
pickle.dump(regressor, random_forest_model_pkl)
# Close the pickle instances
random_forest_model_pkl.close()

#python save_model_pickle.py

# Loading the saved decision tree model pickle
random_forest_model_pkl = open(random_forest_pkl_filename, 'rb')
random_forest_model = pickle.load(random_forest_model_pkl)
print ("Loaded random forest model :: ", random_forest_model)







#    Testing Part

# new user code starts
#dataset= pd.read_csv("/home/buzafar/Documents/simulation_data_latest.csv")
dataset_updated= pd.read_csv("/home/tupevarj/Projects/MachineLearning/simulation_data_7.csv")



# NEW
data_frame_testing = pd.read_csv("/home/tupevarj/Projects/MachineLearning/simulation_data_5.csv")
data_frame_wo_nan = data_frame_testing[np.isfinite(data_frame_testing['RSRQ1'])]

# GET VALUES FOR PREDICTIONS AND USER LOCATIONS
data_testing = data_frame_wo_nan[["RSRP1", "RSRQ1", "RSRP2", "RSRQ2", "RSRP3", "RSRQ3", "RSRP4", "RSRQ4"]]
data_locations = data_frame_wo_nan[["LocationX", "LocationY"]]

# PREDICT VALUES
predicted_values = random_forest_model.predict(np.asarray(data_testing))


dataset_basestations= pd.read_csv("/home/tupevarj/Projects/MachineLearning/basestations.csv")
data_frame_nearest_bs = pd.DataFrame(columns=['BS', "Prediction"])

# CALCULATE NEAREST BASESTATION
for i, user in data_locations.iterrows():
    min_dist = sys.float_info.max
    min_bs_id = -1
    for j, bs in dataset_basestations.iterrows():
        distance = math.sqrt(((bs["LocationX"] - user["LocationX"]) ** 2) + ((bs["LocationY"] - user["LocationY"]) ** 2))
        if distance < min_dist:
            min_dist = distance
            min_bs_id = j+1
    data_frame_nearest_bs = data_frame_nearest_bs.append({'BS': int(min_bs_id), "Prediction": predicted_values[i-105]}, ignore_index=True)


predictions_sum_for_bs = list()

for i in range(0, 7):
    predictions_sum_for_bs.append(data_frame_nearest_bs.loc[data_frame_nearest_bs['BS'] == i+1]["Prediction"].sum())

# Converting RSRP and RSRQ values into floats
array_xx2 = []   #####
array_xx = []
#array_y = []

#print (array_x.shape)

i_max = len(dataset_updated)
print(i_max)
for i in range(0, i_max):
    row = []
    row2 = []
    skip = False
    dataset_row = dataset_updated.iloc[i]
    for j in range(0, 12):
        value = float(dataset_row[j])
        if not j == 2 and not j == 3:
            if not np.isnan(value):
                row.append(float(dataset_row[j]))
            else:
                skip = True
        if j > 3:
            if not np.isnan(value):
                row2.append(float(dataset_row[j]))
            else:
                skip = True
    if not skip:
        array_xx.append(row)
        array_xx2.append(row2)
       # array_y.append(dataset_row[10])



#XX_train, XX_test= train_test_split(array_xx,test_size = 0.3, random_state=0)


#new_prediction = regressor.predict(np.asarray(X_test))

new_prediction = random_forest_model.predict(np.asarray(array_xx2))


# We get new predictions

# Read basestation locations
dataset_basestations= pd.read_csv("/home/tupevarj/Projects/MachineLearning/basestations.csv")  # TODO: read data from csv file

bsatations= []

for i in range(0, 7):
    dict_base_station = dict()
    dict_base_station['base_station_id'] = dataset_basestations['Basestation'][i]
    dict_base_station['LocationX'] = dataset_basestations['LocationX'][i]
    dict_base_station['LocationY'] = dataset_basestations['LocationY'][i]
    string_cell_ids = dataset_basestations['CellIDs'][i].split(',')
    ids_int = list()
    for id in range(0, 3):
        ids_int.append(int(string_cell_ids[id]))
    dict_base_station['Cellids'] = ids_int
    bsatations.append(dict_base_station)



# Calculate distance and set each user to one basestation

for i in range(0,len(array_xx2)):    #  rows
    pb=array_user[i][2],array_user[i][3]
    # row = []
    min_distance = sys.float_info.max
    base_station_id = -1
    all_distances = []
    for station in range(0, 7):   # base stations columns
        pa = bsatations[station]["LocationX"], bsatations[station]["LocationY"]
        distance = math.sqrt(((pa[0] - pb[0]) ** 2) + ((pa[1] - pb[1]) ** 2))
        all_distances.append(distance)
        if distance < min_distance:
            min_distance = distance
            base_station_id = station + 1


    Matrix.append(all_distances)

    l.append([array_user[i][0],array_user[i][1],base_station_id,min_distance])











#print (new_prediction)


# finding abnormal users

store_new_prediction=[]
new_prediction_lenght=len(new_prediction)
print (new_prediction_lenght)
for i in range (0,new_prediction_lenght):
    store_new_prediction.append(new_prediction[i])

print(store_new_prediction)
index_values=[]
for i in range(0,len(store_new_prediction)):
    if store_new_prediction[i]>= 0.1:
        print (store_new_prediction[i])
        #index_values.append([dataset.iloc[i]["Time"], dataset.iloc[i]["UserID"], store_new_prediction[i]])
        #index_values.append([XX_test[i][0], XX_test[i][1], store_new_prediction[i]])
        index_values.append([array_xx[i][0], array_xx[i][1], store_new_prediction[i]]) # handle this problem
#print (index_values)   # user loc + user id + predicted value

#print (index_values)

#  new code  for new z-score
# z-scores for testing

dataset_basestations= pd.read_csv("/home/tupevarj/Projects/MachineLearning/basestations.csv")  # TODO: read data from csv file

bsatations= []

for i in range(0, 7):
    dict_base_station = dict()
    dict_base_station['base_station_id'] = dataset_basestations['Basestation'][i]
    dict_base_station['LocationX'] = dataset_basestations['LocationX'][i]
    dict_base_station['LocationY'] = dataset_basestations['LocationY'][i]
    string_cell_ids = dataset_basestations['CellIDs'][i].split(',')
    ids_int = list()
    for id in range(0, 3):
        ids_int.append(int(string_cell_ids[id]))
    dict_base_station['Cellids'] = ids_int
    bsatations.append(dict_base_station)


array_user = []

for i in range(0,len(index_values)):
    id_user = int(index_values[i][1]) - 1
    time_stamp = index_values[i][0]  # 200 milliseconds

    adfs = time_stamp / 0.3
    int_adfs = int(adfs)
    modulo = adfs % int_adfs
    if modulo > 0.5:
        adfs = math.ceil(adfs)
    else:
        adfs = int_adfs
    actual_index = int(105 * (adfs-1) + id_user)
   # if index_values[i][0]== dataset_stimulation.iloc[actual_index][0] and index_values[i][1]== dataset_stimulation.iloc[actual_index][1]:
    # time , USERID,  Location X , Location Y
    array_user.append([dataset_updated.iloc[actual_index][0],dataset_updated.iloc[actual_index][1],dataset_updated.iloc[actual_index][2],dataset_updated.iloc[actual_index][3]])


l=[]      # list to store user_id,basestation_id,computed distance, time of user
Matrix=[]


for i in range(0,len(array_user)):    #  rows
    pb=array_user[i][2],array_user[i][3]
    # row = []
    min_distance = sys.float_info.max
    base_station_id = -1
    all_distances = []
    for station in range(0, 7):   # base stations columns
        pa = bsatations[station]["LocationX"], bsatations[station]["LocationY"]
        distance = math.sqrt(((pa[0] - pb[0]) ** 2) + ((pa[1] - pb[1]) ** 2))
        all_distances.append(distance)
        if distance < min_distance:
            min_distance = distance
            base_station_id = station + 1


    Matrix.append(all_distances)

    l.append([array_user[i][0],array_user[i][1],base_station_id,min_distance])


dict_users_per_bs = dict()
for i in range(0, 7):
   dict_users_per_bs["BS" + str(i+1)] = 0
# for i in range(0,7):
#     if dict_users_per_bs_[i]< dict_users_per_bs[i] and zscore_new[i] > zscore_ref[i] :
#     # print("base sation",str(i+1))
#     # print (zscore_new[i],"zscore_new")
#     # print(zscore_ref[i],"zscore_ref")
#     #if zscore_new[i] > zscore_ref[i] :
#         print ("outage at BaseStation", i+1)
new_users_total=[]
for i in range(0 ,len(l)):
    key = "BS" + str(l[i][2])
    dict_users_per_bs[key] += 1


for i in range(0,7):    # storing new users total score per BS in a list
    total_score1 = dict_users_per_bs['BS' + str(i + 1)]
    new_users_total.append(total_score1)

print(dict_users_per_bs)
print(new_users_total)


# calculate z-score
bs_users_total=[]
new_mean=[]
zscore_new = list()
for i in range (0,7):
    total_score = dict_users_per_bs['BS'+str(i+1)]
    bs_sum = 0
    bs_users_total.append(bs_sum)
    array_store = list()
    for j in range(0, 7):
        if not j == i:
            array_store.append(dict_users_per_bs["BS" + str(j+1)])
            bs_sum += dict_users_per_bs["BS" + str(j+1)]

    bs1_mean = bs_sum / 6.0
    new_mean.append(bs1_mean)
    differences = ([x - bs1_mean for x in array_store])
    sq_differences = [d ** 2 for d in differences]
    ssd = sum(sq_differences)
    variance = float(ssd / 6.0)  # six basestations

    var = variance/bs_sum
    zscore_new.append(abs(total_score - bs1_mean) / math.sqrt(variance))

#bs_users_total.append(bs_sum)




Basest=[1,2,3,4,5,6,7]
fig = plt.figure()
plt.bar(Basest, zscore_new, label="Abnormal Users", color='b')
plt.legend()
plt.xlabel('Base Stations')
plt.ylabel('z-scores')
plt.title('Mapping of Abnormal Users to the Base Stations')
plt.show()

#  new users code ended

# code for reference zero-score


# code for reference users
store_pred=[]
y_pred_lenght=len(y_pred)
for i in range (0,y_pred_lenght):
    store_pred.append(y_pred[i])

index_values_ref=[]
for i in range(0,len(store_pred)):
    if store_pred[i]>= 0.1:
        #print ( store_pred[i])
        index_values_ref.append([X_test[i][0], X_test[i][1], store_pred[i]])

#print (index_values)   # user loc + user id + predicted value    abnormal users

# TODO: SORT???


dataset_stimulation= pd.read_csv("/home/tupevarj/Projects/MachineLearning/training.csv")
array_user_ = []

for i in range(0,len(index_values_ref)):
    id_user_ = int(index_values_ref[i][1]) - 1
    time_stamp_ = index_values_ref[i][0]  # 200 milliseconds

    adfss = time_stamp_ / 0.2
    int_adfs = int(adfss)
    modulo = adfss % int_adfs
    if modulo > 0.5:
        adfss = math.ceil(adfss)
    else:
        adfss = int_adfs
    actual_index = int(105 * (adfss-1) + id_user_)
   # if index_values[i][0]== dataset_stimulation.iloc[actual_index][0] and index_values[i][1]== dataset_stimulation.iloc[actual_index][1]:
    array_user_.append([dataset.iloc[actual_index][0],dataset.iloc[actual_index][1],dataset.iloc[actual_index][2],dataset.iloc[actual_index][3]])


ll=[]      # list to store user_id,basestation_id,computed distance, time of user
Matrix_=[]


for i in range(0,len(array_user_)):    #  rows
    pb=array_user_[i][2],array_user_[i][3]
    # row = []
    min_distance = sys.float_info.max
    base_station_id = -1
    all_distances = []
    for station in range(0, 7):   # base stations columns
        pa = bsatations[station]["LocationX"], bsatations[station]["LocationY"]
        distance = math.sqrt(((pa[0] - pb[0]) ** 2) + ((pa[1] - pb[1]) ** 2))
        all_distances.append(distance)
        if distance < min_distance:
            min_distance = distance
            base_station_id = station + 1


    Matrix_.append(all_distances)

    ll.append([array_user_[i][0],array_user_[i][1],base_station_id,min_distance])


dict_users_per_bs_ = dict()     # donot need to repeat
for i in range(0, 7):
   dict_users_per_bs_["BS" + str(i+1)] = 0


for i in range(0 ,len(ll)):
    key = "BS" + str(ll[i][2])
    dict_users_per_bs_[key] += 1
print("reference value")
print (dict_users_per_bs_)

ref_users_total=[]
for i in range(0,7):  # storing total scores of users on each base station in a list
    #print ("refrence users per BS")
    total_score2 = dict_users_per_bs_['BS' + str(i + 1)]
    ref_users_total.append(total_score2)


print (ref_users_total)

# calculate z-score
ref_mean=[]
zscore_ref = list()
for i in range (0,7):
    total_score = dict_users_per_bs_['BS'+str(i+1)]
    bs_sum = 0
    array_store = list()
    for j in range(0, 7):
        if not j == i:
            array_store.append(dict_users_per_bs_["BS" + str(j+1)])
            bs_sum += dict_users_per_bs_["BS" + str(j+1)]
            bs1_mean = bs_sum / 6.0

    differences = ([x - bs1_mean for x in array_store])
    sq_differences = [d ** 2 for d in differences]
    ssd = sum(sq_differences)
    variance = float(ssd / 6.0)  # six basestations
    varr= variance/bs_sum
    zscore_ref.append(abs(total_score - bs1_mean) / math.sqrt(variance))
    #print ("bs1_mean+ref",bs1_mean)
    ref_mean.append(bs1_mean)
#print ("array store", array_store)

print ("total ref mean", ref_mean)

Basest=[1,2,3,4,5,6,7]
fig = plt.figure()
plt.bar(Basest, zscore_ref, label="Abnormal Users", color='g')
plt.legend()
plt.xlabel('Base Stations')
plt.ylabel('reference z-scores')
plt.title('Mapping of Abnormal Users to the Base Stations')
plt.show()

# objects = Basest
# y_pos = np.arange(len(objects))
# performance = z1score
#
# plt.bar(y_pos, performance, align='center', alpha=0.5)
#
# plt.xticks(y_pos, objects)
# plt.ylabel('z-scores')
# plt.title('Mapping of Abnormal Users to the Base Stations')
#
# plt.show()
# #fig.savefig('zero-score.png')


#  outage detection   # compare for each base stations
# if z-score_new > z-score_ref
#if zscore_new >
maximum_value= ['BS0', -1]
for i in range(0,len(new_users_total)):
        if maximum_value[1] < new_users_total[i]:
            maximum_value[1] = new_users_total[i]
            maximum_value[0] = 'BS' + str(i+1)


for i in range(0,7):
    if zscore_new[i] >= zscore_ref[i]:
        if  new_users_total[i]==maximum_value[1]:
            print("base sation",str(i+1))
            print (zscore_new[i],"zscore_new")
            print(zscore_ref[i],"zscore_ref")
            print("outage at BaseStation", i + 1)

        # if zscore_new[i] > zscore_ref[i] :
        #     print ("outage at BaseStation", i+1)




# ref user < new nsers

#print ("new users per BS")
#print(dict_users_per_bs)
# print("reference value")
# print (dict_users_per_bs_)



# lets try