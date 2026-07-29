def yes_no(question: str) -> bool:
    while True:
        answer = input(question + " (y/n): ")
        if answer.lower() == "y":
            return True
        elif answer.lower() == "n":
            return False