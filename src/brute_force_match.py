
def match(pattern, text):
    print(len(text))

    for i in range (len(text) - len(pattern)):

        for j in range(len(text) - len(pattern)):

            for k in range(len(pattern)):

                for l in range(len(pattern)):

                    print(pattern[k][l])
                


if __name__ == "__main__":
    match([[0]],
        [[0, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 0, 2]]
    )

