###
# hangman.py
# 
# A hangman guesser implementation that utilizes principles from information theory, namely the
# concept of Shannon's information entropy. See paper.pdf for more details on the implementation.
# 
# To play, run hangman.py with python3.
# The game will ask for the number of characters in your word or phrase (including spaces). Then,
# the game will keep guessing letters (or for the first guess, a space). If the letter doesn't
# appear in your word or phrase, enter "N" to indicate as such. Otherwise, enter "Y" followed by a
# comma, followed by a comma-separated list of where the letter appears. For example, if my word is
# "HELLO" and the program guesses "L" then I will enter "Y, 3, 4" to respond.
# 
# Jerry Chen
# March 2017
###
# import re # regex
import math
# import itertools

FREQ_FILE = "word_freq.txt"

# Get the dictionary from a given text file, filtering out non-alphanumeric
# entries just in case.
def load_freqs(filename):
    freq_file = open(filename, 'r')
    all_freqs = freq_file.read().rstrip().split('\n') # word followed by count
    freq_file.close()

    # make all uppercase dictionary
    all_freqs = list(map(lambda entry: entry.upper(), all_freqs))
    all_freqs = [entry.split() for entry in all_freqs]
    for entry in all_freqs:
        entry[1] = int(entry[1])
 
    return all_freqs

# Calculates the total frequency of words in dictionaries, to be used for weighting different words.
def get_total_weight(dictionaries):
    total = 0
    for inp_dict in dictionaries:
        for entry in inp_dict:
            total += entry[1]
    return total


# Counts how many times a letter appears in a word.
def letter_count(letter, word):
    count = 0
    for c in word:
        if (c == letter):
            count += 1

    return count


# Function to calculate letter frequencies based on given input dictionary parameter.
# Letter frequency not by how many times a letter appears but rather by how many words
# in the dictionary contain the letter
# Input: List of words
# Returns: List of tuples of (letter, frequency), sorted by frequency
def dict_freq(dictionaries):
    global guessed_letters
    letter_freqs = {}
    for i in range(65, 65+26):
        letter_freqs[chr(i)] = 0

    total_weight = get_total_weight(dictionaries)

    # multiple dictionaries, want letter frequency from all combined
    for i in range(65, 65+26): # ascii values of uppercase letters
        letter = chr(i)
        if (not(letter in guessed_letters)): # make sure it hasn't been guessed already
            for inp_dict in dictionaries:
                probs = [entry[1] for entry in inp_dict]
                h = entropy(probs)
                for entry in inp_dict:
                    for c in entry[0]:
                        if (c == letter):
                            letter_freqs[letter] += h*entry[1]/total_weight # *h

    return sorted(list(letter_freqs.items()),
        key = lambda x: x[1], reverse = True)

# Guess a letter and return a response in the format "N" for no or "Y" followed
# by locations of the letter in the word.
def guess_letter(letter):
    global num_guesses
    global guessed_letters
    global last_guess
    guessed_letters.append(letter)
    last_guess = letter

    response = input(
        "Guess #{0}: Is there a(n) {1}?\n".format(num_guesses, letter)
        ).rstrip().split(', ')

    response_type = response[0].upper();

    while (response_type != 'N' and response_type != 'Y'):
        response = input("Please begin your response with Y/N: ").rstrip().split(', ');
        response_type = response[0].upper();

    num_guesses += 1
    return response

# Guesses an entire phrase rather than a single letter, expecting either "Y" or "N" as a response.
def guess_phrase(phrase):
    global guessed_phrases
    global last_guess
    
    guessed_phrases.append(phrase)
    last_guess = phrase

    response = input(
        "Guess #{0}: Is the phrase {1}?\n".format(num_guesses, phrase)
        ).rstrip().split(', ')
    response_type = response[0].upper();

    while (response_type != 'N' and response_type != 'Y'):
        response = input("Please enter Y/N: ").rstrip().split(', ');
        response_type = response[0].upper();

    return response

# Returns a list of the starting locations of each word, starting at position 1
def split_phrase(phrase_length):
    # Need to split the phrase into its respective words by guessing for the spaces
    space_response = guess_letter('space')
    word_positions = [1] # regardless of spaces, first word will be at pos 1
    if (space_response[0].upper() == 'Y'):
        for pos in space_response[1:]:
            word_positions.append(int(pos) + 1)

    return word_positions

# find which word is referred to by a given position
def which_word(pos, num_words, word_positions):
    for i in range(num_words-1, -1, -1):
        if (pos >= word_positions[i]):
            return i

# Given a discrete probability distribution, calculates the entropy of the random variable.
def entropy(probs):
    h = 0
    for p in probs:
        if (p != 0):
            h += p*math.log2(1/p)
    return h

# Calculates the joint entropy of a set of random variables.
def joint_entropy(probs_list):
    h = 0
    for probs in probs_list:
        h += entropy(probs)

    return h

# Normalizes dictionary frequencies to add to 1.
def normalize_dicts(dictionaries):
    # global num_words
    temp = list(dictionaries)
    for i in range(len(temp)):
        my_dict = temp[i]
        total_weight = get_total_weight([my_dict])
        for j in range(len(my_dict)):
            my_dict[j][1] = my_dict[j][1]/total_weight
        temp[i] = my_dict

    return temp

# Updates dictionaries and weights after a guess, given its response.
def iterate(letter, response, dictionaries):
    global num_words, word_positions

    temp = list(dictionaries)
    if (response[0].upper() == 'Y'):
        # filter dictionaries based on guess
        modified = [False for i in range(num_words)] # forgot why i need this but i do...
        counts = {}
        for word_num in range(num_words):
            counts[word_num] = 0

        for pos in response[1:]:
            pos = int(pos)
            word_num = which_word(pos, num_words, word_positions)
            counts[word_num] += 1
            modified[word_num] = True
            rel_pos = pos - word_positions[word_num] + 1 # position relative to start of word
            cur_dict = temp[word_num]
            cur_dict = list(filter(lambda entry: 
                entry[0][rel_pos-1] == letter, cur_dict))
            temp[word_num] = cur_dict

            phrase[pos-1] = letter
        for i in range(num_words):
            cur_dict = temp[i]
            if (not modified[i]):
                cur_dict = list(filter(lambda entry:
                    not (letter in entry[0]), cur_dict))
            cur_dict = list(filter(lambda entry:
                letter_count(letter, entry[0]) == counts[i], cur_dict))
            temp[i] = cur_dict

    if (response[0] == 'N'):
        for i in range(num_words):
            my_dict = temp[i]
            my_dict = list(filter(lambda entry:
                not (letter in entry[0]), my_dict))
            temp[i] = my_dict
    return temp

#############################################
# SET UP FOR THE GAME #
log = open("log.txt", "w")
num_guesses = 1 # increment with each guess
num_words = 0 # default value but will update later
last_guess = ""

guessed_letters = [] # add guesses here
guessed_phrases = []

# Ask user for length of phrase
phrase_length = int(input("How many characters in this phrase?\n"))
phrase = list('*' * phrase_length)

# Split the phrase into its words, saving the # of words and positions/lengths of each word
word_positions = split_phrase(phrase_length)
num_words = len(word_positions)
for i in range(1, num_words):
    phrase[word_positions[i]-2] = " "
word_positions.append(phrase_length + 2) # just for convenience b/c i'm too lazy to think of a better way to get length of last word
word_lengths = [
    word_positions[i+1] - (word_positions[i] + 1) for i in range(num_words)
    ]

print ("Phrase: " + "".join(phrase))
# Get the dictionaries for each word
raw_dict = load_freqs(FREQ_FILE)

dictionaries = [
    list(filter(lambda entry:
        len(entry[0]) == word_length, raw_dict)) for word_length in word_lengths
    ]

########################################
# ACTUAL GAME

while ('*' in phrase):
    log.write("----------------------------------\n")
    log.write("AFTER GUESS #{0} ({2}): {1}\n".format(num_guesses-1, "".join(phrase),
        last_guess))

    dictionaries = normalize_dicts(dictionaries)
    letter_freqs = dict_freq(dictionaries)

    for i in range(num_words):
        my_dict = dictionaries[i]
        h = entropy([entry[1] for entry in my_dict])
        if (h <= 0.075):
            my_dict = [my_dict[0]]
            dictionaries[i] = my_dict
        log.write("Dictionary for word {0}: {1}\n".format(i+1, my_dict[:10]))
        # log.write("weight for this dict: {0}\n".format(get_total_weight([my_dict])))
        log.write("entropy for this dict: {0}\n".format(h))

    dictionaries = normalize_dicts(dictionaries)
    H_dicts = joint_entropy(
                [[entry[1] for entry in my_dict] for my_dict in dictionaries]
                )

    log.write("Joint entropy for dictionaries: {0}\n".format(H_dicts))
    log.write("10 most frequent letters: {0}\n".format(letter_freqs[:10]))

    if (H_dicts <= 0.075): # approximately 95% confidence in guessing the phrase
        my_phrase = " ".join([my_dict[0][0] for my_dict in dictionaries])
        response = guess_phrase(my_phrase)
        if (response[0] == 'Y'):
            phrase = my_phrase
            break
        else:
            num_guesses += 3

    # print (letter_freqs)
    # determine some criteria whether to guess entire phrase or a letter
    response = guess_letter(letter_freqs[0][0])
    dictionaries = iterate(letter_freqs[0][0], response, dictionaries)

    print ("".join(phrase))
    print ("----------------------------------")


log.write("----------------------------------\n")
log.write("AFTER GUESS #{0} ({2}): {1}\n".format(num_guesses, "".join(phrase),
    last_guess))
for i in range(num_words):
    my_dict = dictionaries[i]
    dict_weight = get_total_weight([my_dict])
    for j in range(len(my_dict)):
        my_dict[j][1] = my_dict[j][1]/dict_weight
    log.write("Dictionary for word {0}: {1}\n".format(i+1, my_dict[:10]))
log.write("Joint entropy for dictionaries: {0}\n".format(
        joint_entropy(
            [[entry[1] for entry in my_dict] for my_dict in dictionaries]
            )))
letter_freqs = dict_freq(dictionaries)
log.write("10 most frequent letters: {0}\n".format(letter_freqs[:10]))










