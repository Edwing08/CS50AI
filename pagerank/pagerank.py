import os
import random
import re
import sys
from numpy.random import choice

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Local dictionary to store data that will be returned
    transition_dic = {}

    # Linked pages within the page
    linked_pages = corpus[page]

    # Number of pages in corpus and number of pages linked within the page
    num_linked_pages = len(linked_pages)
    num_pages = len(corpus.keys())

    # If the current page has no linked pages, set the same probability to all pages
    if num_linked_pages == 0:
        equal_prob = 1/num_pages
    # Otherwise, set probability acording to the damping factor
    else:
        # dampling factor, surfer choosing one of the links from the page
        lp_value = damping_factor/num_linked_pages

        # 1 - dampling_factor, surfer choosing one of the links among all pages
        negative_df = 1 - damping_factor
        equal_prob = negative_df/num_pages

    # returns a dictionary, where each key corresponds to each page of the corpus and each value represents the probability of that page being chosen
    for key in corpus:
        transition_dic[key] = equal_prob

        if key in corpus[page]:
            transition_dic[key] += lp_value

    return transition_dic


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Obtain the list of pages from the corpus
    pages = list(corpus.keys())

    # Dictionary to store PageRank values
    page_rank = {}

    # Initially every page start with 0 
    for page in pages:
        page_rank[page] = 0
    
    # First page is chosen randomly with the same probability
    pick = random.choice(pages)

    # Iterate n sample times
    for i in range(n):
        
        # Use the transition model function to obtain the probability distribution, given the page
        result = transition_model(corpus, pick, damping_factor)

        result_pages = list(result.keys())
        result_prob_values = list(result.values())

        # Randomly choose a page based on the probability obtained from the transition model function
        pick = choice(result_pages, 1, p=result_prob_values)
        pick = pick[0]

        # Keep track the number of times every page has been chosen
        page_rank[pick] += 1

    # Obtain the PageRank, divide each counter with the number of samples
    for key, count in page_rank.items():
        page_rank[key] = count/n

    return page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Obtain the list of pages from the corpus
    pages = list(corpus.keys())

    # Check if any of the pages does not link to any other page. If that is true, consider the page to link every page in the corpus
    for corpus_key, corpus_value in corpus.items():
        if len(corpus_value) == 0:
            corpus[corpus_key] = set(corpus.keys())

    # Dictionary to store PageRank values
    page_rank = {}

    # Number of pages in the corpus
    num_pages = len(corpus.keys())

    # 1 - dampling_factor
    negative_df = 1 - damping_factor
    initial_state = negative_df/num_pages

    # Set the initial state of the PageRank
    for page in pages:
        page_rank[page] = initial_state

    # Loop until every PageRank value converge, with difference between previous and new value less than 0,001
    difference = True
    while(difference):

        # Variable to keep track of the number of pages that has converged
        count_diff = 0

        # Iterate through every element in the corpus
        for key, page in corpus.items():
            # Initialice the sumation variable
            sumation = 0
            
            # Iterate through every element in the corpus once again
            for i_key, i_value in corpus.items():
                
                # Seach if the page is linked by another page in the corpus and apply the relation and add the result to the sumation
                if key in i_value:
                    sumation += page_rank[i_key]/len(corpus[i_key])

            # Pagerank using the formula            
            new_page_rank = negative_df/num_pages + damping_factor*sumation

            # Count the number of pages that has converged
            if (new_page_rank - page_rank[key]) < 0.001:
                count_diff += 1
            
            # Update the values from the PageRank
            page_rank[key] = new_page_rank

        # Leave the while loop if every page has converged
        if count_diff == num_pages:
            difference = False

    return page_rank


if __name__ == "__main__":
    main()
