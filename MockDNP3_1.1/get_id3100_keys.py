# -*- coding: utf-8 -*-
"""
idq_loader v1
Phil Evans, ORNL
1/27/2019
"""

# Modified by Davis Arthur on 7/10/2019

from pathlib import Path
import random
import hashlib
#import pickle

def chunks(l, n):
        # For item i in a range that is a length of l,
        for i in range(0, len(l), n):
            # Create an index range for l of n items:
            yield l[i:i+n]

def initial_load(id3100_filename):

    ## define key file name and path; check to see if it exists
    id3100_keyfile = Path(str(id3100_filename))

    if id3100_keyfile.is_file():
        id3100_keyfile = open(id3100_keyfile, "r")
        id3100_data = id3100_keyfile.readlines()
    else:
        print("Error: id3100_filename", str(id3100_filename), "does not exist. Run QKD!")
        return

    ## is one of the lines called "KEY"? if so, the key data is on the next line!
    for i in range(0, len(id3100_data)):
        if "KEY" in id3100_data[i]:
            id3100_secretkeys = id3100_data[i+1]
            print("id3100 secret keys found. Loading", len(id3100_secretkeys), "secret bits")

    ## id3100 chunk and key table generate
    chunked_id3100keys_new = list(chunks(id3100_secretkeys, 256))
    num_id3100keys_new = len(chunked_id3100keys_new)

    if len(chunked_id3100keys_new[num_id3100keys_new-1]) != 256:
        print("Last id3100 key not complete... deleting")
        del chunked_id3100keys_new[-1]
        num_id3100keys_new = num_id3100keys_new-1

    print(num_id3100keys_new, "256-bit id3100 keys loaded!")

    num_id3100keys = num_id3100keys_new
    chunked_id3100keys = chunked_id3100keys_new

    # using the first QKD key to initialize a random seed to generate a 64-bit key index start
    key_index_id3100_init = int(chunked_id3100keys[0],2)
    random.seed(key_index_id3100_init)
    key_index_id3100_start = random.getrandbits(64)

    # create new key table
    key_index_id3100 = [(key_index_id3100_start+i) for i in range(0,num_id3100keys-1)]
    key_str_id3100 = [chunked_id3100keys[i] for i in range(0, num_id3100keys-1)]
    key_value_id3100 = [int(chunked_id3100keys[i],2) for i in range(0,num_id3100keys-1)]
    key_sha256_id3100 = [hashlib.sha256(chunked_id3100keys[i].encode('utf-8')).hexdigest() for i in range(0,num_id3100keys-1)]
    key_status_id3100 = [False for i in range(0,num_id3100keys-1)]
    key_table_id3100 = [key_index_id3100,key_str_id3100,key_value_id3100,key_sha256_id3100,key_status_id3100]

    return key_table_id3100


def refresh(id3100_filename,key_table_id3100):

    ## define key file name and path; check to see if it exists
    id3100_keyfile = Path(str(id3100_filename))

    if id3100_keyfile.is_file():
        id3100_keyfile = open(id3100_keyfile, "r")
        id3100_data = id3100_keyfile.readlines()
    else:
        print("Error: id3100_filename", str(id3100_filename), "does not exist. Run QKD!")
        return

    ## is one of the lines called "KEY"? if so, the key data is on the next line!
    for i in range(0, len(id3100_data)):
        if "KEY" in id3100_data[i]:
            id3100_secretkeys = id3100_data[i]
            print("id3100 secret keys found. Loading", len(id3100_secretkeys), "secret bits")

    ## id3100 chunk and key table generate
    chunked_id3100keys_new = list(chunks(id3100_secretkeys, 256))
    num_id3100keys_new = len(chunked_id3100keys_new)

    ## If the file has been appended, first key value should be the same...
    if key_table_id3100[1][0] == int(chunked_id3100keys_new[0],2):
        print("Generating updated key list")

        ## ...so we'll just refresh the whole damn thing
        if len(chunked_id3100keys_new[num_id3100keys_new-1]) != 256:
            print("Last id3100 key not complete... deleting")
            del chunked_id3100keys_new[-1]
            num_id3100keys_new = num_id3100keys_new-1

        print(num_id3100keys_new, "256-bit id3100 keys loaded!")

        num_id3100keys = num_id3100keys_new
        chunked_id3100keys = chunked_id3100keys_new

        # using the first QKD key to initialize a random seed to generate a 64-bit key index start
        key_index_id3100_init = int(chunked_id3100keys[0],2)
        random.seed(key_index_id3100_init)
        key_index_id3100_start = random.getrandbits(64)

        # create new key table
        key_index_id3100 = [(key_index_id3100_start+i) for i in range(0,num_id3100keys-1)]
        key_value_id3100 = [int(chunked_id3100keys[i],2) for i in range(0,num_id3100keys-1)]
        key_sha256_id3100 = [hashlib.sha256(chunked_id3100keys[i].encode('utf-8')).hexdigest() for i in range(0,num_id3100keys-1)]
        key_status_id3100 = [False for i in range(0,num_id3100keys-1)]
        key_table_id3100 = [key_index_id3100,key_value_id3100,key_sha256_id3100,key_status_id3100]

        return key_table_id3100

        ## Since first key values are different, we have a completely new key file
    else:
        print("This keyfile is new. Importing secret bits...")

        ## load new key and append to the existing table.
        if len(chunked_id3100keys_new[num_id3100keys_new-1]) != 256:
            print("Last id3100 key not complete... deleting")
            del chunked_id3100keys_new[-1]
            num_id3100keys_new = num_id3100keys_new-1

        num_id3100keys_old = len(key_table_id3100[0])
        num_id3100keys = num_id3100keys_old + num_id3100keys_new

        print(num_id3100keys_new, "more 256-bit id3100 were added")
        print(num_id3100keys, "256-bit id3100 keys are available!")

        # extend new key values etc., to existing table

        key_index_id3100_new = [key_table_id3100[0][-1] + i for i in range(0,num_id3100keys_new-1)]
        key_value_id3100_new = [int(chunked_id3100keys_new[i],2) for i in range(0,num_id3100keys_new-1)]
        key_sha256_id3100_new = [hashlib.sha256(chunked_id3100keys_new[i].encode('utf-8')).hexdigest() for i in range(0,num_id3100keys_new-1)]
        key_status_id3100_new = [False for i in range(0,num_id3100keys_new-1)]

        key_table_id3100[0].extend(key_index_id3100_new)
        key_table_id3100[1].extend(key_value_id3100_new)
        key_table_id3100[2].extend(key_sha256_id3100_new)
        key_table_id3100[3].extend(key_status_id3100_new)

        return key_table_id3100
