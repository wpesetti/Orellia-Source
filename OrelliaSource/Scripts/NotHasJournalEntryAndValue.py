def main(entryTag, valueString):
    if(Interface.HasJournalEntryAndValue(entryTag, valueString)):
        return False
    else:
        return True