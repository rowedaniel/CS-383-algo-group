#Ian Cebula, Daniel Neshyba-Rowe, Elliot Mayer, Alex David Skiles

def match(pattern, text):
    # pattern_xor is the XOR of the integers in the pattern
    pattern_xor = 0
    for a in range(len(pattern)):
        for b in range(len(pattern)):
            pattern_xor = pattern_xor ^ pattern[a][b]

    # search_xor is the XOR of the integers in a pattern-sized portion of the text, initialized
    # as the XOR of the top-leftmost portion
    search_xor = 0
    for a in range(len(pattern)):
        for b in range(len(pattern)):
            search_xor = search_xor ^ text[a][b]
    
    SEARCH_BOUNDARY = len(text) - len(pattern) + 1

    for i in range(SEARCH_BOUNDARY):
        for j in range(SEARCH_BOUNDARY):
            # If the pattern XOR matches the current search XOR, search through the current section
            # of the text by brute force
            #print("i:" + str(i) + " / j:" + str(j) + " / search_xor:" + str(search_xor))
            if pattern_xor == search_xor:
                match_is_good = True
                for k in range(len(pattern)):
                    for l in range(len(pattern)):
                        if pattern[k][l] != text[i + k][j + l]:
                            match_is_good = False
                            break
                    if not match_is_good:
                        break
                if match_is_good:
                    return i, j
            # If there wasn't a match, update the search XOR for the next iteration of the loop
            # If j is at the search boundary...
            if j == SEARCH_BOUNDARY - 1:
                # ...and i is too, you've gone through the entire text without finding the pattern, so you return None
                if i == SEARCH_BOUNDARY - 1:
                    return None
                # ...and i isn't, then set the search XOR to be the XOR of the leftmost pattern-sized portion
                # of the text that is 1 row below this one
                search_xor = 0
                for a in range(len(pattern)):
                    for b in range(len(pattern)):
                        search_xor = search_xor ^ text[i+a+1][b]
                continue
            # Otherwise, XOR out the integers on the left side of the search XOR, and XOR in the integers directly
            # to the right of the search XOR
            for x in range(len(pattern)):
                search_xor = search_xor ^ text[i+x][j]
                search_xor = search_xor ^ text[i+x][j+len(pattern)]


if __name__ == "__main__":
    m = match([[1,0],[1,1]],
        [[1, 1, 0, 0],
        [1, 0, 1, 0],
        [1, 1, 1, 1],
        [1, 1, 1, 1]]
    )
    print(m)
