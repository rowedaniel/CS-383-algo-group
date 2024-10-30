
def match(pattern, text):

    for i in range (len(text) - len(pattern)+1):

        for j in range(len(text) - len(pattern)+1):

            match_is_good = True
            for k in range(len(pattern)):

                for l in range(len(pattern)):

                    print(pattern[k][l])
                    if (pattern[k][l] != text[i+k][j+l]):
                        match_is_good = False
                        break
                if not match_is_good:
                    break
            if match_is_good:
                return i,j
    return None



if __name__ == "__main__":
    m = match([[1,1],[1,1]],
        [[0, 1, 1, 1],
        [0, 1, 1, 1],
        [1, 1, 1, 1],
        [0, 1, 0, 1]]
    )

