

A considerable number of experiments have been carried out to fix the most optimal parameters in order to obtain the best performance that can be achieved by this specific model. The following list briefly describes some of the values used. Each parameter was modified one by one so that its impact on the performance of the model could be clearly seen.

- one convolutional layer with 30, 60 and 90 filters with (2,2), (3,3) and (4,4) as kernel size
- one pooling layer with (2,2), (3,3) and (4,4) as poolsize
- Adding one convolutional and one pooling layer after the previous ones, with the previous characteristics
- one hidden layer with 60, 150 and 220 neurons and then adding another hidden layer with 60, 150 and 220 neurons
- 0.2, 0.5 and 0.7 dropout

One important observation is that the addition of another set of convolutional and pooling layer make the most important contribution in the overall learning process, increasing the accuracy considerably. One thing of note is that when two convolutional and pooling layers are used, the number of filters in the second convolution layer should be larger than the first one.

The best number of neurons was 150 particulartly in this problem, below than that the learning process was weaker and abode than that there was no substantial improvement, in fact, the model experienced some overfitting. Adding another hidden layer did not help either. It was essential to add dropout to avoid overfitting, it was clearly notable.  