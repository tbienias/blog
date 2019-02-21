# Understanding Naive Bayes using Python and Pandas #

### 05/08/2018 ###

Naive Bayes is one of the simplest and most common classification methods in machine learning. In this blog post we don't want to focus on all the mathematical stuff, but instead we're going to implement our own quick'n'dirty Naive Bayes solution using Python and [Pandas](https://pandas.pydata.org/). We will get some training data, apply _Laplace Smoothing_ a.k.a. _1-Up Smoothing_ and classify an unseen record of data.

## [](#data)Data
### [](#training-data)Training Data
Our stakeholders gave us the following data for trainig purposes:

| Department     | Age   | Salary  | Status | Count |         
|:---------------|:------|:--------|:-------|:------|
| Sales          | 31-35 | 46K-50K | Senior | 30    |
| Sales          | 26-30 | 26K-30K | Junior | 40    |
| Sales          | 31-35 | 31K-35K | Junior | 40    |
| IT             | 21-25 | 46K-50K | Junior | 20    |
| IT             | 31-35 | 66K-70K | Senior |  5    |
| IT             | 26-30 | 46K-50K | Junior |  3    |
| IT             | 41-45 | 66K-70K | Senior |  3    |
| Marketing      | 36-40 | 46K-50K | Senior | 10    |
| Marketing      | 31-35 | 41K-45K | Junior |  4    |
| Administration | 46-50 | 36K-40K | Senior |  4    |
| Administration | 26-30 | 26K-30K | Junior |  6    |

So our predictors are 

* Department
* Age
* Salary

whilst our target is _Status_.

### [](#create-dataframe)Create Dataframe
Let's put our dataset into a Pandas `DataFrame`. For this we import Pandas and create a `DataFrame` object:

```python
import pandas as pd


td = pd.DataFrame({'Department': ['Sales', 'Sales', 'Sales',
                                 'IT', 'IT', 'IT', 'IT',
                                 'Marketing', 'Marketing',
                                 'Administration', 'Administration'],
                   'Age': ['31-35', '26-30', '31-35', '21-25', '31-35', 
                          '26-30', '41-45', '36-40', '31-35', '46-50',
                          '26-30'],
                   'Salary': ['46K-50K', '26K-30K', '31K-35K', '46K-50K',
                            '66K-70K', '46K-50K', '66K-70K', '46K-50K',
                            '41K-45K', '36K-40K', '26K-30K'],
                   'Status': ['Senior', 'Junior', 'Junior', 'Junior',
                            'Senior', 'Junior', 'Senior', 'Senior',
                            'Junior', 'Senior', 'Junior'],
                   'Count': [30, 40, 40, 20, 5, 3, 3, 10, 4, 4, 6]},
                  columns=['Department', 'Age', 'Salary', 'Status', 'Count'])
```

### [](#prior-probabilities)Prior Probabilities
Sweet, so now that we have our data in memory it's time calculate the prior probabilities.
We do this by grouping the _Status_ column and summing up the counts for each. After that we divide the counts of each target by the total number of counts:

```python
prior_junior, prior_senior = td.groupby(['Status']).Count.sum() / td.Count.sum()
```

This holds `0.6848484848484848` (~68%) for Junior and `0.3151515151515151` (~32%) for Senior.

## [](#adjustments)Adjustments
### [](#distinct-features)Exploring distinct Features
We need to split our data into distinct feature tables so that we can see whether or not we need to add missing bins or if we have to apply any smoothing. 

We do this by creating a list containing all of our predictors. Then we group by the predictor in question and _Status_, sum up the counts and unstack the outcome so that our _Status_ values get a new column for Junior and Senior.
In the end we apply some cosmetics by resetting the index and deleting the axis label:

```python
cols = ['Department', 'Age', 'Salary']
feature_list = [td.groupby([col, 'Status']).Count.sum().unstack(fill_value=0).
    reset_index().rename_axis(None, axis='columns') for col in cols]
```

Now `feature_list` contains the following tables:

| Department     | Junior | Senior |         
|:---------------|:-------|:-------|
| Administration | 6      | 4      |
| IT             | 23     | 8      |
| Marketing      | 4      | 10     |
| Sales          | 80     | 30     |

| Age   | Junior | Senior |         
|:------|:-------|:-------|
| 21-25 | 20     | 0      |
| 26-30	| 49     | 0      |
| 31-35	| 44     | 35     |
| 36-40	| 0      | 10     |
| 41-45	| 0      | 3      |
| 46-50	| 0      | 4      |

| Salary  | Junior | Senior |         
|:--------|:-------|:-------|
| 26K-30K | 46     | 0      |
| 31K-35K | 40     | 0      |
| 36K-40K | 0      | 4      |
| 41K-45K | 4      | 0      |
| 46K-50K | 23     | 40     |
| 66K-70K | 0      | 8      |

### [](#missing-bins)Missing Bins
Examining the tables above one could argue that we have some missing bins in the _Age_ and _Salary_ table. 
Let's define which bins are not included. 

For the _Age_ table there go:

* 51-55
* 56-60
* 61-65

and for the _Salary_ table we identify:

* 21K-25K
* 51K-55K
* 56K-60K
* 61K-65K

The problem with missing bins is that if we get an unseen record of data relating to one of the missing bins the whole Bayes Expression will evaluate to zero.

In order to tackle this problem we insert the missing bins into our data by defining new `DataFrame` objects containing the missing bins. Then we concatenate them with their respective feature tables and sort the resulting `DataFrame` objects by their predictor column:

```python
department_bins = pd.DataFrame()

age_bins = pd.DataFrame({'Age': ['51-55', '56-60', '61-65'],
                   'Junior': [0, 0, 0],
                   'Senior': [0, 0, 0]},
                   columns=['Age', 'Junior', 'Senior'])

salary_bins = pd.DataFrame({'Salary': ['21K-25K', '51K-55K', '56K-60K', '61K-65K'],
                   'Junior': [0, 0, 0, 0],
                   'Senior': [0, 0, 0, 0]},
                   columns=['Salary', 'Junior', 'Senior'])

bin_list = [department_bins, age_bins, salary_bins]

adjusted_list = [pd.concat([feature_df, bin_df]).sort_values(by=[col]).reset_index(drop=True)
                 for feature_df, bin_df, col in zip(feature_list, bin_list, cols)]
``` 

Doing so yields in the following tables:

| Department     | Junior | Senior |         
|:---------------|:-------|:-------|
| Administration | 6      | 4      |
| IT             | 23     | 8      |
| Marketing      | 4      | 10     |
| Sales          | 80     | 30     |

| Age   | Junior | Senior |         
|:------|:-------|:-------|
| 21-25 | 20     | 0      |
| 26-30	| 49     | 0      |
| 31-35	| 44     | 35     |
| 36-40	| 0      | 10     |
| 41-45	| 0      | 3      |
| 46-50	| 0      | 4      |
| 51-55	| 0      | 0      |
| 56-60	| 0      | 0      |
| 61-65	| 0      | 0      |

| Salary  | Junior | Senior |         
|:--------|:-------|:-------|
| 21K-25K | 0      | 0      |
| 26K-30K | 46     | 0      |
| 31K-35K | 40     | 0      |
| 36K-40K | 0      | 4      |
| 41K-45K | 4      | 0      |
| 46K-50K | 23     | 40     |
| 51K-55K | 0      | 0      |
| 56K-60K | 0      | 0      |
| 61K-65K | 0      | 0      |
| 66K-70K | 0      | 8      |

This looks good enough. Now we head over to smooth the values of our `DataFrame` objects.

### [](#laplace-smoothing)Laplace Smoothing
To motivate why we need to smooth our values we bring up a little example. 
Lets say we would want to predict the _Status_ given the following predictors:

* Administration 
* 51-55
* 46K-50K

This would result in the following expressions:

`P(Junior) * P(Administration | Junior) * P(51-55 | Junior) * P(46K-50K | Senior)`

and 

`P(Senior) * P(Administration | Senior) * P(51-55 | Senior) * P(46K-50K | Senior)`

The problem in here is that `P(51-55 | _Status_)` will always be zero because we have no occurrence for _51-55_ in our _Age_ table and therefore the whole expression evaluates to zero. This leads to the fact that we can't make a prediction since Junior and Senior will both be zero.

For that reason we will apply _Laplace Smoothing_ a.k.a. _1-Up Smoothing_ by iterating all of our feature tables and checking if we have any zeroes in our Senior and Junior columns. If so we raise every value in the respective column by 1:

```python
for df in adjusted_list:
    if any(df.Senior == 0):
        df.Senior += 1
    if any(df.Junior == 0):
        df.Junior += 1
```

And thats basically our _Laplace Smoothing_. Let's see how this turned out:

| Department     | Junior | Senior |         
|:---------------|:-------|:-------|
| Administration | 6      | 4      |
| IT             | 23     | 8      |
| Marketing      | 4      | 10     |
| Sales          | 80     | 30     |

| Age   | Junior | Senior |         
|:------|:-------|:-------|
| 21-25 | 21     | 1      |
| 26-30	| 50     | 1      |
| 31-35	| 45     | 36     |
| 36-40	| 1      | 11     |
| 41-45	| 1      | 4      |
| 46-50	| 1      | 5      |
| 51-55	| 1      | 1      |
| 56-60	| 1      | 1      |
| 61-65	| 1      | 1      |

| Salary  | Junior | Senior |         
|:--------|:-------|:-------|
| 21K-25K | 1      | 1      |
| 26K-30K | 47     | 1      |
| 31K-35K | 41     | 1      |
| 36K-40K | 1      | 5      |
| 41K-45K | 5      | 1      |
| 46K-50K | 24     | 41     |
| 51K-55K | 1      | 1      |
| 56K-60K | 1      | 1      |
| 61K-65K | 1      | 1      |
| 66K-70K | 1      | 9      |

Mission accomplished - everything smoothed out! We see that in our _Department_ table we didn't do anything as there were no zeroes whilst the other tables got smoothed.

## [](#towards-prediction)Towards Prediction
### [](#calculate-likelihoods)Calculate Likelihoods
In this step we need to compute all the likelihoods for our features. We do this by dividing each cell in every target column by the total amount of occurrences of that column:

```python
for df in adjusted_list:
    df.Junior /= df.Junior.sum()
    df.Senior /= df.Senior.sum()
```

That's it! All likelihoods are computed - let's have a look at the tables:

| Department     | Junior | Senior |         
|:---------------|:-------|:-------|
| Administration | 0.053097      | 0.076923      |
| IT             | 0.203540     | 0.153846      |
| Marketing      | 0.035398      | 0.192308     |
| Sales          | 0.707965     | 0.576923    |

| Age   | Junior | Senior |         
|:------|:-------|:-------|
| 21-25 | 0.172131     | 0.016393      |
| 26-30	| 0.409836     | 0.016393      |
| 31-35	| 0.368852     | 0.590164     |
| 36-40	| 0.008197      | 0.180328     |
| 41-45	| 0.008197    | 0.065574      |
| 46-50	| 0.008197      | 0.081967      |
| 51-55	| 0.008197      | 0.016393      |
| 56-60	| 0.008197      | 0.016393      |
| 61-65	| 0.008197      | 0.016393      |

| Salary  | Junior | Senior |         
|:--------|:-------|:-------|
| 21K-25K | 0.008130      | 0.016129      |
| 26K-30K | 0.382114     | 0.016129      |
| 31K-35K | 0.333333     | 0.016129      |
| 36K-40K | 0.008130      | 0.080645      |
| 41K-45K | 0.040650      | 0.016129      |
| 46K-50K | 0.195122     | 0.661290     |
| 51K-55K | 0.008130      | 0.016129      |
| 56K-60K | 0.008130     | 0.016129     |
| 61K-65K | 0.008130      | 0.016129     |
| 66K-70K | 0.008130      | 0.145161      |

### [](#staple)Staple DFs together
Since we don't want to hustle around with different `DataFrame` objects we staple them together. 
We do so by renaming each `DataFrame`s feature column to _Feature_ and concatenate our `DataFrame` objects:

```python
[[df.rename(columns={col:'Feature'}, inplace=True) for df in adjusted_list] for col in cols]

likelihood_table = pd.concat(adjusted_list).reset_index(drop=True)
```

So now we have our super likelihood lookup-table:

| Feature     | Junior | Senior |         
|:---------------|:-------|:-------|
| Administration | 0.053097      | 0.076923      |
| IT             | 0.203540     | 0.153846      |
| Marketing      | 0.035398      | 0.192308     |
| Sales          | 0.707965     | 0.576923    |
| 21-25 | 0.172131     | 0.016393      |
| 26-30	| 0.409836     | 0.016393      |
| 31-35	| 0.368852     | 0.590164     |
| 36-40	| 0.008197      | 0.180328     |
| 41-45	| 0.008197    | 0.065574      |
| 46-50	| 0.008197      | 0.081967      |
| 51-55	| 0.008197      | 0.016393      |
| 56-60	| 0.008197      | 0.016393      |
| 61-65	| 0.008197      | 0.016393      |
| 21K-25K | 0.008130      | 0.016129      |
| 26K-30K | 0.382114     | 0.016129      |
| 31K-35K | 0.333333     | 0.016129      |
| 36K-40K | 0.008130      | 0.080645      |
| 41K-45K | 0.040650      | 0.016129      |
| 46K-50K | 0.195122     | 0.661290     |
| 51K-55K | 0.008130      | 0.016129      |
| 56K-60K | 0.008130     | 0.016129     |
| 61K-65K | 0.008130      | 0.016129     |
| 66K-70K | 0.008130      | 0.145161      |

### [](#predict)Predict
We're almost there! We just need a `predict()` function which will take our predictors as input, look up the right values from our lookup-table and spit out the Bayes values for Junior and Senior respectively. We already stated the formulas in [this section](#laplace-smoothing) so there's no need to do it again - let's get it on:

```python
def predict(department, age, salary):
    junior_value = \
        prior_junior * \
        likelihood_table.loc[likelihood_table.Feature == department].Junior.item() * \
        likelihood_table.loc[likelihood_table.Feature == age].Junior.item() * \
        likelihood_table.loc[likelihood_table.Feature == salary].Junior.item()
    senior_value = \
        prior_senior * \
        likelihood_table.loc[likelihood_table.Feature == department].Senior.item() * \
        likelihood_table.loc[likelihood_table.Feature == age].Senior.item() * \
        likelihood_table.loc[likelihood_table.Feature == salary].Senior.item()
    return junior_value, senior_value

j1, s1 = predict('Sales', '26-30', '46K-50K')
j2, s2 = predict('IT', '21-25', '66K-70K')
```

Let's take a look at our values. Basically we did:

`P(Junior) * P(Sales | Junior) * P(26-30 | Junior) * P(46K-50K | Junior) = 0.03877236983994281`

`P(Senior) * P(Sales | Senior) * P(26-30 | Senior) * P(46K-50K | Senior) = 0.001971059083697899`

which tells us that _Sales_ aging in-between _26-30_ and earning _46K-50K_ will be categorized as Junior. Our second prediction for _IT_ aging in-between _21-25_ and earning _66k-70k_ will also be categorized as Junior by:

`P(Junior) * P(IT | Junior) * P(21-25 | Junior) * P(66k-70k | Junior) = 0.0001950734857572123`

`P(Senior) * P(IT | Senior) * P(21-25 | Senior) * P(66k-70k | Senior) = 0.00011537906831402338`

## [](#conclusion)Conclusion
And this is it! Our Naive Bayes implementation using Python and Pandas is finished and now we have a basic understanding of what steps are necessary to get a Naive Bayes computation up and running. If you like to play around with this implementation I've uploaded the Jupyter-Notebook to my [Github](https://gitlab.com/JACKSONMEISTER/understanding-naive-bayes). Anyways if you want to use Naive Bayes in a production environment I'd suggest that you use a rock solid implementation like the one from [scikit-learn](http://scikit-learn.org/stable/) instead of going on your own.