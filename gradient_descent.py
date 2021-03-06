import numpy as np
import matplotlib.pyplot as plt

from parameters import filename
from parameters import gradient_descent as parameters
from parameters import cross_val_folds
from cross_validation import cross_val_split
import prepare_data
from metrics import nrmse


def predict (features, weights_vector):
    return [sum([weight * feature_val for weight, feature_val in zip(weights_vector, features[i])]) for i in range(len(features))]


def gradient_descent(parameters):
    train_losses, test_losses = [], []
    training_object_count, feature_count, training_features, training_labels, test_features, test_labels\
        = prepare_data.read_from_file(filename)

    training_features, training_labels = prepare_data.prepare_data(training_features, training_labels)
    test_features, test_labels = prepare_data.prepare_data(test_features, test_labels)

    train_data = np.hstack((training_features, np.reshape(training_labels, (-1, 1))))

    weights = np.random.rand(feature_count + 1)

    for iteration in range(parameters['num_iterations']):
        print('Iteration {}. {}-fold cross-validation:'.format(iteration + 1, cross_val_folds))

        for cross_val_iteration in range(cross_val_folds):
            cross_val_training_features, cross_val_test_features, \
            cross_val_training_labels, cross_val_test_labels = cross_val_split(train_data, cross_val_folds)

            cross_val_training_features = np.hstack((cross_val_training_features, np.ones((cross_val_training_features.shape[0], 1), dtype=cross_val_training_features.dtype)))
            cross_val_test_features = np.hstack((cross_val_test_features, np.ones((cross_val_test_features.shape[0], 1), dtype=cross_val_test_features.dtype)))

            predicted_values = predict(cross_val_training_features, weights)

            absolute_error = [predicted_value - cross_val_training_label for predicted_value, cross_val_training_label in zip(predicted_values, cross_val_training_labels)]

            gradient = cross_val_training_features.T.dot(absolute_error) / cross_val_training_features.shape[0] + parameters['regularization_strength'] * weights

            weights = weights * (1 - parameters['learning_rate'] * parameters['regularization_strength']) + parameters['learning_rate'] * (-gradient)

            predicted_labels = predict(cross_val_test_features, weights)
            train_loss = nrmse(predicted_labels, cross_val_test_labels)
            train_losses.append(train_loss)
            print('Cross validation loss: {}'.format(train_loss))

            predicted_labels = predict(test_features, weights)
            test_loss = nrmse(predicted_labels, test_labels)
            test_losses.append(test_loss)
            print('Test loss: {}'.format(test_loss))

    return train_losses, test_losses, parameters
