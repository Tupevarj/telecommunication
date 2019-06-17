
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import pandas as pd
from sklearn import manifold


# In[2]:


# read csv
df = pd.read_csv("training.csv")


# In[3]:


type(df)


# In[4]:


df[:2]


# In[5]:


df.dropna(axis=0, how="any", inplace=True)


# In[6]:


df.drop(df.columns[:4], axis=1, inplace=True)


# In[7]:


df[:2]


# In[8]:


y = df["Label"]


# In[9]:


X = df.drop(df.columns[-1], axis=1)


# In[10]:


X[:4]


# In[11]:


# signalX = X.dropna(axis=0, how="any")


# In[12]:


# signalX[:4]


# In[13]:



# apply MDS dimension reduction to signalDF, with only 3 dimensions left
mds = manifold.MDS(3, max_iter=200, n_init=1)


# In[14]:


len(X)


# In[ ]:



threeDimSig = mds.fit_transform(X)


# In[ ]:


threeDimSig[:5]


# In[ ]:




rng = np.random.RandomState(42)

# Generate train data
X = 0.3 * rng.randn(100, 2)
X_train = np.r_[X + 2, X - 2]
# Generate some regular novel observations
X = 0.3 * rng.randn(20, 2)
X_test = np.r_[X + 2, X - 2]
# Generate some abnormal novel observations
X_outliers = rng.uniform(low=-4, high=4, size=(20, 2))

# fit the model
clf = IsolationForest(max_samples=100, random_state=rng)
clf.fit(X_train)
y_pred_train = clf.predict(X_train)
y_pred_test = clf.predict(X_test)
y_pred_outliers = clf.predict(X_outliers)

# plot the line, the samples, and the nearest vectors to the plane
xx, yy = np.meshgrid(np.linspace(-5, 5, 50), np.linspace(-5, 5, 50))
Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

plt.title("IsolationForest")
plt.contourf(xx, yy, Z, cmap=plt.cm.Blues_r)

b1 = plt.scatter(X_train[:, 0], X_train[:, 1], c='white',
                 s=20, edgecolor='k')
b2 = plt.scatter(X_test[:, 0], X_test[:, 1], c='green',
                 s=20, edgecolor='k')
c = plt.scatter(X_outliers[:, 0], X_outliers[:, 1], c='red',
                s=20, edgecolor='k')
plt.axis('tight')
plt.xlim((-5, 5))
plt.ylim((-5, 5))
plt.legend([b1, b2, c],
           ["training observations",
            "new regular observations", "new abnormal observations"],
           loc="upper left")
plt.show()

