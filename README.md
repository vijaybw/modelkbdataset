# modelkb-dataset
This Flask App would process the dataset 
and return top 10 features and its correlation with each other .

1. Upload dataset with csv format with first line as columns.

2. Program would automatically identify the column data types.

3. And then it would calculate top 10 features through kbest method 
https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.SelectKBest.html

4. Also, we show the correlation among top 10 features so that users can study all the 10 features and its relationships with each other.