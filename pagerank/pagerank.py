import os
import random
import re
import sys
import copy

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
    prob = corpus.copy()
    if len(corpus[page]) == 0:
        for p in corpus:
            prob[p] = 1/len(corpus)
        return prob
        
    for p in corpus:
        prob[p] = (1-damping_factor)/len(corpus)
    for linkedPage in corpus[page]:
        prob[linkedPage] += (damping_factor)/len(corpus[page])

    return prob


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    dist = dict()
    for x in corpus:
        dist[x] = 0
    prev = None
    for i in range(n):
        if prev is not None:
            ret = transition_model(corpus, prev, damping_factor)
            probs = list(ret.values())
            keys = list(ret.keys())
            a = random.choices(keys, weights=probs)[0]
            dist[a] += 1
            prev = a
        else:
            prev = random.choice(list(corpus))
            dist[prev] +=1
    for p in dist:
        dist[p] = dist[p]/n
    return dist




def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    old = {}
    curr = {}

    for page in corpus:
        old[page] = 1/len(corpus)

    while True:

        for page in corpus:
            sum = 0
            damping = (1-damping_factor)/len(corpus)
            for p2 in corpus:
                if page in corpus[p2]:
                    sum += (old[p2] / len(corpus[p2]))
                if len(corpus[p2]) == 0:
                    sum += (old[p2] / len(corpus))

            sum *= damping_factor
            sum += damping
            curr[page] = sum

        difference = [abs(curr[x] - old[x]) for x in corpus]
        maximum = max(difference)
        if maximum < 0.001:
            break
        old = curr.copy()

    return old
    

if __name__ == "__main__":
    main()
