# Reddit .zst to SQLite Importer

This Python script streams, decompresses, and imports Reddit .zst data (from sources like Pushshift) into a SQLite database using efficient batch insertion.

---

## How to Use

### 1. Get the Code

Fork, clone, or download the files from this repository.

### 2. Install Requirements

Install the required Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 3. Download Data (via Academic Torrents)

The Pushshift Reddit dataset is archived on Academic Torrents, which requires a torrent client. The data is available at:  
[academictorrents.com/details/1614740ac8c94505e4ecb9d88be8bed7b6afddd4](https://academictorrents.com/details/1614740ac8c94505e4ecb9d88be8bed7b6afddd4)

**Important:** This is a multi-terabyte archive. In your torrent client, de-select all files and then select only the specific `.zst` files you need.

- `RC_...zst`: Reddit Comments
- `RS_...zst`: Reddit Submissions

### 4. File Structure

The script scans a `subreddits/` folder. Create this directory and place your `.zst` files inside it.

```
your-project/
├── reddit_import_script.py
│
└── subreddits/
    ├── RS_2023-01.zst
    ├── RC_2023-01.zst
    └── ... (all your .zst files)
```

### 5. Run the Importer

Execute the script from your terminal:

```bash
python reddit_import_script.py
```

The script will:
- Create a database file named `reddit_data.db` in your project directory
- Automatically detect all `.zst` files in the `subreddits/` folder
- Show real-time progress as data is imported
- Print a final summary with total submissions and comments imported

**Example output:**
```
Creating database...
Database created

Found 1 submission file(s)
File size: 924.78 MB
Importing submissions from subreddits/RS_2023-01.zst...
  Imported 1000 submissions...
  Imported 2000 submissions...
  ...
✓ Imported 50000 submissions (0 errors)

IMPORT COMPLETE!
Total submissions: 50,000
Total comments: 150,000
Database saved to: reddit_data.db
```

---

## Warning: Database File Size

The resulting SQLite database will be **significantly larger** than the compressed `.zst` files:

- **Expansion ratio:** Expect the `.db` file to be upto **10x larger** than the compressed source

**Before importing, ensure you have sufficient disk space available.** Monitor your available storage throughout the import process, especially when working with large comment files.

---

