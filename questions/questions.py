import nltk
import sys
import os
from nltk.tokenize import word_tokenize
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1

nltk.download('punkt')
nltk.download('stopwords')

def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    # Get the path to the folder containing all the files
    current_path = os.getcwd()
    path = os.path.join(current_path, directory)
    
    files = {}

    # Read and store in a dictionary the content of each file, the key corresponds to the title of the file and the value to the content itself.
    for file in os.listdir(path):
        path_file = os.path.join(path, file)

        with open(path_file, encoding='utf8') as document:
            files[file] = document.read()

    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    
    list_words = word_tokenize(document)
  
    preprocessed_list = []

    # Check every word if the word contains alphabetic characters and transform to lowercase any word with uppercase characters
    for word in list_words:
        # Transform to lowercase any word with uppercase characters
        word_lower = word.lower()

        # Consider just the important words, leave behind the words regarding puntuation and stopwords.
        if any((c not in string.punctuation) for c in word_lower) and word_lower not in nltk.corpus.stopwords.words("english"):
            preprocessed_list.append(word_lower)
        else:
            continue
  
    return preprocessed_list


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    IDF_values = {}

    num_documents = len(documents)

    for document_words in documents.values():

        # Temporaty list to store if the word has already appeared in the document
        temp_list = []

        # Count if a word appears at least one time in a document
        for word in document_words:

            if word not in IDF_values:
                IDF_values[word] = 1
                temp_list.append(word)
            
            elif word in IDF_values and word not in temp_list:
                IDF_values[word] += 1
                temp_list.append(word)

    # Calculate the idf score of each word according to the equation
    for word in IDF_values:
        IDF_values[word] = math.log(num_documents/IDF_values[word])

    return IDF_values


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    record = {}

    for file, words_in_file in files.items():
        record[file] = 0

        # Count the number of times a word from the query appears in a document
        # Multiply the number of times the word appears by the idf score of the given word
        for word in query:
            if word in words_in_file:                
                number = words_in_file.count(word)
                record[file] += idfs[word]*number

    # Sort the files according to the tf-idf score.
    sorted_list = sorted(record.items(), key=lambda x:x[1], reverse=True)

    top_files = [file[0] for file in sorted_list]

    return top_files[0:n]    


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    record = {}

    for sentence, content in sentences.items():
        # Keep the record of each sentence in a dictionary. 
        # The key correspond to the sentence itself and the value a list with two slots. the first one is the idfs score and the second is the query term density.
        record[sentence] = [0, 0]

        # If the word in query is present in the sentence, add the idf score to the total score of the sentence.
        for word in query:
            if word in content:
                record[sentence][0] += idfs[word]
                record[sentence][1] += 1
        
        # Calculate the query term density of each sentence
        record[sentence][1] = record[sentence][1]/len(content)

    # Sort the sentences, first according to the idfs and second according to the query term density.
    sorted_list = sorted(record.items(), key=lambda x:x[1], reverse=True)

    top_sentences = [sentence[0] for sentence in sorted_list if sentence[1] == sorted_list[0][1]]

    top_sentences = top_sentences[0:n]

    return top_sentences


if __name__ == "__main__":
    main()
