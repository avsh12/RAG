def chunk(filename: str) -> list[str]:
    with open(filename, "r") as file:
        text_db: list[str] = file.readlines()
        text_db: list[str] = [x.strip("\n") for x in text_db]
    return text_db
