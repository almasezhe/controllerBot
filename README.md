Simple telegram bot for personal use

1. Whisper for recognizing and transcribing audio messages
2. Note taker with embeddings and vector search via FAISS
3. Everything stored locally, sqlite3
4. Financial Tracker
   /note <text> | for saving a note
   /search <text> for searching in notes
   /addrecord amount<int> name<text> description<text> category<text> account<text> | to add financial record
   /deleterecord id<int> | to delete financial record
   /last | to show 10 last records
   /total | summarize and show every bank account