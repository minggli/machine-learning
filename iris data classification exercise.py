import tensorflow as tf
from tensorflow.contrib import learn
from sklearn import metrics, cross_validation, naive_bayes, preprocessing, pipeline, linear_model, tree, decomposition
from sklearn.datasets import load_iris
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import warnings
from sklearn.externals.six import StringIO
from mpl_toolkits.mplot3d import Axes3D
import statsmodels.api as sm
from minglib import gradient_descent
import pydotplus
warnings.filterwarnings('ignore')

data = load_iris()


def visualize():

    iris = load_iris()

    X = iris.data  # we only take the first two features.
    Y = iris.target

    space = .5

    x_min, x_max = X[:, 0].min() - space, X[:, 0].max() + space
    y_min, y_max = X[:, 1].min() - space, X[:, 1].max() + space

    plt.figure(1, figsize=(12, 6))

    # Plot the training points
    plt.subplot(1, 2, 1)
    plt.scatter(X[:, 0], X[:, 1], c=Y, cmap=plt.cm.Paired)
    plt.xlabel(iris['feature_names'][0])
    plt.ylabel(iris['feature_names'][1])
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks()
    plt.yticks()

    x_min, x_max = X[:, 2].min() - space, X[:, 2].max() + space
    y_min, y_max = X[:, 3].min() - space, X[:, 3].max() + space

    plt.subplot(1, 2, 2)
    plt.scatter(X[:, 2], X[:, 3], c=Y, cmap=plt.cm.Paired)
    plt.xlabel(iris['feature_names'][2])
    plt.ylabel(iris['feature_names'][3])
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks()
    plt.yticks()

    # To getter a better understanding of interaction of the dimensions
    # plot the first three PCA dimensions
    #
    # fig = plt.figure(3, figsize=(8, 6))
    # ax = Axes3D(fig, elev=-150, azim=110)
    # X_reduced = decomposition.PCA(n_components=3).fit_transform(iris.data)
    # ax.scatter(X_reduced[:, 0], X_reduced[:, 1], X_reduced[:, 2], c=Y,
    #            cmap=plt.cm.Paired)
    # ax.set_title("First three PCA directions")
    # ax.set_xlabel("1st eigenvector")
    # ax.w_xaxis.set_ticklabels([])
    # ax.set_ylabel("2nd eigenvector")
    # ax.w_yaxis.set_ticklabels([])
    # ax.set_zlabel("3rd eigenvector")
    # ax.w_zaxis.set_ticklabels([])
    plt.show()


visualize()

target_dict = {'species': {k: v for k, v in enumerate(data['target_names'])}}

df = pd.DataFrame(data['data'], columns=data['feature_names'], dtype=float) \
    .join(
    pd.DataFrame(data['target'], columns=['species'], dtype=int)).replace(target_dict)

df['species'] = pd.Categorical.from_array(df['species']).codes
df['species'] = df['species'].astype('category')

regressors = df.select_dtypes(include=['float'])
regressand = df.select_dtypes(include=['category'])


def normalize(data):
    # building a scaler that applies to future data
    col_name = data.columns
    scaler = preprocessing.StandardScaler().fit(data)
    return pd.DataFrame(scaler.transform(data), columns=col_name)

# Decision Tree classifier
reg = tree.DecisionTreeClassifier(max_depth=3, max_leaf_nodes=20, min_samples_leaf=15, random_state=2)

x_train, x_test, y_train, y_test = \
    cross_validation.train_test_split(regressors, np.array(regressand), test_size=.3)

reg.fit(X=x_train, y=y_train)

kf_gen = cross_validation.KFold(df.shape[0], n_folds=5, shuffle=False, random_state=2)

prediction = reg.predict(x_test)
accuracy = metrics.accuracy_score(y_test, prediction)
print('Single Tree Accuracy: {:.4f}'.format(accuracy))

# with pd.ExcelWriter('iris_pred.xlsx') as writer:
#     df.to_excel(writer, sheet_name='output', index=False)

dot_data = StringIO()
tree.export_graphviz(reg, feature_names=regressors.columns, class_names=target_dict['species'], filled=True, \
                     rounded=True, special_characters=True, out_file=dot_data)

graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
graph.write_pdf("iris.pdf")



# logistic regression
lr = linear_model.LogisticRegression()
lr.fit(x_train, y_train)
prediction = lr.predict(x_test)
score = metrics.accuracy_score(y_test, prediction)
print('Logistic Regression Accuracy: {:.4f}'.format(score))

# Bayesian

clf = naive_bayes.GaussianNB()
clf.fit(x_train, y_train)
prediction = lr.predict(x_test)
score = metrics.accuracy_score(y_test, prediction)
print('Bayesian (GaussianNB) Accuracy: {:.4f}'.format(score))


## Tensorflow Neutral Network implementation


def main(unused_argv):

    iris = learn.datasets.load_dataset('iris')
    x_train, x_test, y_train, y_test = cross_validation.train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42)

    # Build 3 layer DNN with 10, 20, 10 units respectively.
    feature_columns = learn.infer_real_valued_columns_from_input(x_train)
    classifier = learn.DNNClassifier(
        feature_columns=feature_columns, hidden_units=[10, 20, 10], n_classes=3)

    # Fit and predict.
    classifier.fit(x_train, y_train, steps=200)
    predictions = list(classifier.predict(x_test, as_iterable=True))
    score = metrics.accuracy_score(y_test, predictions)
    print('Accuracy: {:.4f}'.format(score))
    # print(y_test, predictions)


if __name__ == '__main__':
  output = tf.app.run()

