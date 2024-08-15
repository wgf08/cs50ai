import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Calculate and return the joint probability.

    The returned probability should represent the likelihood that:
        * everyone in the set `one_gene` has one copy of the gene,
        * everyone in the set `two_genes` has two copies of the gene,
        * everyone not in sets `one_gene` or `two_genes` does not have the gene,
        * everyone in the set `have_trait` has the trait, and
        * everyone not in set `have_trait` does not have the trait.
    """
    parents = set()
    children = set()

    for person in people:
        if people[person]['mother'] is None:
            parents.add(person)
        else:
            children.add(person)

    antes = 1
    for person in parents:
        num = 1 * (person in one_gene) + 2 * (person in two_genes)
        have = (person in have_trait)
        antes *= PROBS["gene"][num] * PROBS["trait"][num][have]

    conses = 1
    for person in children:
        mom = people[person]["mother"]
        dad = people[person]["father"]
        num = 1 * (person in one_gene) + 2 * (person in two_genes)
        num_mom = 1 * (mom in one_gene) + 2 * (mom in two_genes)
        num_dad = 1 * (dad in one_gene) + 2 * (dad in two_genes)
        have = (person in have_trait)
        mutation = PROBS["mutation"]

        if num == 0:
            if num_dad == 0 and num_mom == 0:
                effect = (1 - mutation) * (1 - mutation)
            elif (num_dad == 2 and num_mom == 2):
                effect = mutation * mutation
            elif (num_dad == 2 and num_mom == 0) or (num_dad == 0 and num_mom == 2):
                effect = mutation * (1 - mutation)
            elif (num_dad == 0 and num_mom == 1) or (num_dad == 1 and num_mom == 0):
                effect = (1 - mutation) * 0.5
            elif (num_dad == 2 and num_mom == 1) or (num_dad == 1 and num_mom == 2):
                effect = mutation * 0.5
            else:
                effect = 0.5 * 0.5
        elif num == 1:
            if (num_dad == 0 and num_mom == 0) or (num_dad == 2 and num_mom == 2):
                effect = mutation * (1 - mutation)
            elif (num_dad == 2 and num_mom == 0) or (num_dad == 0 and num_mom == 2):
                effect = (1 - mutation) * (1 - mutation) + mutation * mutation
            elif (num_dad == 1 and num_mom == 1):
                effect = 2 * 0.5 * 0.5
            else:
                effect = mutation * 0.5 + (1 - mutation) * 0.5
        else:
            if num_dad == 0 and num_mom == 0:
                effect = mutation * mutation
            elif (num_dad == 2 and num_mom == 2):
                effect = (1 - mutation) * (1 - mutation)
            elif (num_dad == 2 and num_mom == 0) or (num_dad == 0 and num_mom == 2):
                effect = mutation * (1 - mutation)
            elif (num_dad == 0 and num_mom == 1) or (num_dad == 1 and num_mom == 0):
                effect = mutation * 0.5
            elif (num_dad == 2 and num_mom == 1) or (num_dad == 1 and num_mom == 2):
                effect = (1 - mutation) * 0.5
            else:
                effect = 0.5 * 0.5
        conses *= effect * PROBS["trait"][num][have]

    return antes * conses

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        num = 1 * (person in one_gene) + 2 * (person in two_genes)
        have = (person in have_trait)
        probabilities[person]["gene"][num] += p
        probabilities[person]["trait"][have] += p
    
    return

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        sum_gene = sum(probabilities[person]["gene"].values())
        for i in range(3):
            probabilities[person]["gene"][i] /= sum_gene

        sum_trait = probabilities[person]["trait"][True] + probabilities[person]["trait"][False]
        probabilities[person]["trait"][True] /= sum_trait
        probabilities[person]["trait"][False] /= sum_trait

    return


if __name__ == "__main__":
    main()
