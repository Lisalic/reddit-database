# Reddit .zst to SQLite Importer

This Python script streams, decompresses, and imports Reddit .zst data (from sources like Pushshift) into a SQLite database using efficient batch insertion.

---

## How to Use

### 1. Get the Code

Clone the repository to your local machine and navigate into the directory:
```
git clone https://github.com/Lisalic/reddit-database.git
cd reddit-database
```
### 2. Install Requirements

Install the required Python packages using the `requirements.txt` file:

```
pip install -r requirements.txt
```
### 3. Acquire the Data

1.  Go to [Academic Torrents](https://academictorrents.com).

2.  Search for `"reddit comments"` or `"reddit submissions"`.

3.  Download the `.torrent` file for the data you want.

4.  Use a torrent client (like [qBittorrent](https://www.qbittorrent.org/)) to open the `.torrent` and download the files.
> **Warning:** The full archive is enormous (above 3 TB). If you try to download the entire torrent, you will likely fill your hard drive. Only select the specific `.zst` files you need using the interface in your torrent client.


### 4. File Structure

You should have a "zst_files" folder in the cloned directory. Once you have downloaded the .zst files through torrent, move them into this folder.

Your file structure should look like this:

```
reddit-database/
├── reddit_import_script.py
│
└── zst_files/
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
- Automatically detect all `.zst` files in the `zst_files/` folder
- Show real-time progress as data is imported
- Print a final summary with total submissions and comments imported

**Example output:**
```
Creating database...
Database created

Found 1 submission file(s)
File size: 924.78 MB
Importing submissions from zst_files/RS_2023-01.zst...
  Imported 1000 submissions...
  Imported 2000 submissions...
  ...
  Imported 50000 submissions (0 errors)

IMPORT COMPLETE!
Total submissions: 50,000
Total comments: 150,000
Database saved to: reddit_data.db
```

---

## Warning: Database File Size

The resulting SQLite database will be **significantly larger**  than the compressed `.zst` files (5-10 times the original file size):

**Before importing, ensure you have sufficient disk space available.** 

---

