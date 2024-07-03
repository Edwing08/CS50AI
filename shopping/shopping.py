from calendar import calendar, month_abbr
import csv
import sys
from turtle import pos

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    
    evidence_gathered = []
    labels_gathered = []
    Months = {"Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3, "May": 4, "June": 5, "Jul": 6, "Aug": 7, "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11}

    # Open the file and read each row
    with open(filename) as datafile:
        data = csv.reader(datafile, delimiter=',')
        row_counter = 0
        for row in data:

            # Omit the header row
            if row_counter == 0 :
                row_counter += 1

            # Store the evidence of each row in a list
            else:
                evidence = []

                # Transform the data to a numeric form and make sure that the data is in the correct format
                for position, item in enumerate(row):
                    if position in [0,2,4,10,11,12,13,14,15,16]:
                        if position == 10:
                            evidence.append(int(Months[item]))
                        elif position == 15:
                            evidence.append(int(0 if item == "FALSE" else  1))
                        elif position == 16:
                            evidence.append(int(0 if item == "FALSE" else  1))
                        else:
                            evidence.append(int(item))

                    elif position in [1,3,5,6,7,8,9]:
                        evidence.append(float(item))

                    elif position == 17:
                        labels_gathered.append(int(0 if item == "FALSE" else  1))
                
                evidence_gathered.append(evidence)

        return (evidence_gathered, labels_gathered)

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """

    # Train using K-nearest neighbour, considering one neighbour (k=1)
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)

    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    true_positive = 0
    true_negative = 0

    # Count how many true positive and true negative predictions were
    for actual, predicted in zip(labels, predictions):
        if actual == 1 and predicted == 1:
            true_positive += 1
            
        elif actual == 0 and predicted == 0:
            true_negative += 1

    # Obtain the number of positive and negative labels in the testing set
    total_positive = labels.count(1)
    total_negative = labels.count(0)

    # Calculate the sensitivity and specificity
    sensitivity = true_positive/total_positive
    specificity = true_negative/total_negative

    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
