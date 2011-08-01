def main(entryTag):
    if(Interface.HasJournalEntry(entryTag)):
        return False
    else:
        return True