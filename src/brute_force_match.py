class match():
    def __init__(self) -> None:
        pass
        
    def match(self, pattern, text):
        self.pattern = pattern
        self.text = text

        for i in range (len(self.text)):

            for j in range (len(self.text) - len(self.pattern))