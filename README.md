-------------------------------------
 CS221 PROJECT README - LEVY ROMANO
-------------------------------------
MACHINE READING FROM A CONTEXTUALIZED
     DATA SOURCE: SPORTS REPORTS
-------------------------------------

Table of Contents
=================

- Code organization
- Data organization
- Libraries
- Using the code


Code organization
============

The code is organized as follows:
- scraping.py holds various methods to scrape the website ESPN, and fetch the game reports, along with various helper methods.
- game.py holds the main class for Games, whose properties leverage the results from scraping to find the answers to various questions.
- dataset.py holds a class and methods to turn a set of games (either from a set or report URLs or from games saved with pickle) into a feature extracted dataset, saved as a dictionary.
- featureExtraction.py holds the various feature extraction methods.
- train.py holds the methods to actually train the model.
- test.py holds the methods to test the model.
- scripts.py holds various methods to actually use the system, and quickly test it.
- textUtil.py contains various helper functions to manipulate text.


Data organization
============

The data is (and must be) organized as follows:
- the directory « games » holds sets of games of various sizes, where multiple games are saved as pickle objects. It also holds the corpus of text used to train word2vec.
- the directory « features » holds saved feature extracted datasets, as well as ‘columns’ files, which are used in the feature extraction process.
- the directory « word2vec » holds the vectors obtained from training word2vec on our corpus.
- the directory « models » holds saved models from various trainings.
All those directories should be in the source directory.


Libraries
===========

The code uses the following external libraries:
- liblinear for training regression models. A ‘liblinear’ directory should be in the source folder, containing the complete library (installed with a make command).
- gensim for the word2vec algorithm.
- nltk and StanfordNER for entity tagging. A ‘NER’ folder should be in source code, cf StanfordNER documentation for more information.


Using the code
==================

- Once all the libraries have been installed, a very simple test can be done by running scripts.py and calling the function simple_test with arguments:
simple_test(‘quick_test’, ‘Who won?’, method=‘skip_1 ‘).
This will quickly scrape a few URLS from a specific date, and train a model using the ‘skip_1’ feature extraction, with the query ‘Who won?’. It can also be used with the queries ‘Who lost?’ or ‘Who scored the [first/second/third/etc.] goal?’ for example. In this method, the console will then interactively ask the user to provide a game report URL to test the model.

A fully automated test can be done with the full_test function, on the same file. The arguments are:
name: the name of the test, can be chosen by the user
query: the question to use, from the set specified above
train_set: the training set of games, that should exist in games/
test_set: the testing set of games, that should exist in games/

Otherwise, the user can freely use the system by:
- scraping games using scrape_games in script.py or automated_scraping/interactive_scraping in scraping.py.
- creating a feature extracted dataset by using the build_and_dump function from dataset.py, using the chosen feature extraction method as one of the arguments.
- training it using the train function from training.py.
- testing it automatically using the test method in test.py, or interactively using run in test.py.


(c) Daniel Levy, Nathanael Romano