"""
This script shows the usage of scikit-learns linear regression functionality.
"""

# %% [markdown]
# # Linear Regression using Scikit-Learn #

# %% [markdown]
# ## Ice Cream Dataset ##

# | Temperature C° | Ice Cream Sales |
# |:--------------:|:---------------:|
# |       15       |        34       |
# |       24       |       587       |
# |       34       |       1200      |
# |       31       |       1080      |
# |       29       |       989       |
# |       26       |       734       |
# |       17       |        80       |
# |       11       |        1        |
# |       23       |       523       |
# |       25       |       651       |

# %% [markdown]
# ### Dependencies ###

# Install Numpy for number crunching and Matplotlib for plotting graphs:

# ```bash
# pip install sklearn
# ```

# %% [markdown]
# ### Imports ###

import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


# %% [markdown]
# ### Ice Cream Dataset as Numpy Array ###

data = np.array([[15, 34],
                 [24, 587],
                 [34, 1200],
                 [31, 1080],
                 [29, 989],
                 [26, 734],
                 [17, 80],
                 [11, 1],
                 [23, 523],
                 [25, 651],
                 [0, 0],
                 [2, 0],
                 [12, 5]])


# %% [markdown]
# ### Plotting the Dataset ###

x_values, y_values = data.T
plt.style.use('ggplot')
plt.scatter(x_values, y_values)
plt.show()


# %% [markdown]
# ### Prepare Train and Test Data ###

x_train, x_test, y_train, y_test = train_test_split(
    x_values, y_values, test_size=1/3)

x_train = x_train.reshape(-1, 1)
x_test = x_test.reshape(-1, 1)
y_train = y_train.reshape(-1, 1)
y_test = y_test.reshape(-1, 1)


# %% [markdown]
# ### Train model ###

regression = linear_model.LinearRegression()
regression.fit(x_train, y_train)


# %% [markdown]
# ### Predict ###

y_prediction = regression.predict(x_test)


# ### Plot Predicted Results and print metrics ###

plt.scatter(x_test, y_test)
plt.plot(x_test, y_prediction, color='blue')
plt.show()

print('Coefficient: \n', regression.coef_)
print('Intercept: \n', regression.intercept_)
print('Mean Squared Error: %.2f' % mean_squared_error(y_test, y_prediction))
