
def match(pattern, text):
    count = 0
    for i in range ((len(text) - len(pattern))+1):
        
        for j in range((len(text) - len(pattern))+1):
            
            match_is_good = True
            for k in range(len(pattern)):
                
                for l in range(len(pattern)):
                    count += 1
                    

                    if (pattern[k][l] != text[i+k][j+l]):
                        match_is_good = False
                        break
                if not match_is_good:
                    break
            if match_is_good:
                return i,j
    return None



if __name__ == "__main__":
    m = match([[4,4],
               [4,4]],

        [[4, 4, 0, 1],
        [3, 4, 4, 1],
        [1, 4, 4, 4],
        [0, 1, 4, 4]]
    )
    print(m)

