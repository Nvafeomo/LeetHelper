#  LeetHelper

A modular CLI tool for tracking, analyzing, and reflecting on LeetCode practice sessions. Powered by Python, built for growth.

---

##  Features

  - Add problems with category, difficulty, status, and link  
  - Record multiple attempts with:
  - Technique used (e.g. brute force, DP)
  - Time spent per attempt
  - Timestamped reflection notes  
  - View average, shortest, and longest solve time per problem  
  - Search problems by approach used  
  - Identify fastest-solved hard problems  
  - Highlight most time-consuming categories  
  - Monitor performance and pacing over time

---

##  Folder Structure
```text
PyProject/
├── main.py
├── problem_tracker.py
├── utils/
│   ├── storage.py
│   ├── time_parse.py
│   └── plot.py         # (Optional for visual features)
├── data/
│   └── problems.json
```
---

##  How to Run

1. Open a terminal in the `PyProject` directory  
2. Run the app:
3. Use the numbered CLI menu to add problems, append notes, and view stats

---

##  Note System

Each problem supports multiple note entries per attempt, including:

- `attempt`: The try number (e.g. "1", "2")  
- `approach`: Strategy used ("brute force", "sliding window")  
- `reflection`: Description of your thought process  
- `time_spent`: Duration (e.g. `"30 minutes"`, `"1.5 hours"`)  
- `timestamp`: Automatically logged when you add the note  

---

##  Analytics

- **View time stats** per problem  
- **Search by approach keyword**  
- **Filter fastest-solved hard problems**  
- **Find slowest categories by average time spent**

Perfect for competitive prep, spaced repetition, and deep reflection.

---

##  Future Ideas

- Visualize performance with `matplotlib`
- Add spaced repetition or revisit tracking
- Export to CSV or Markdown for publishing

---

##  Getting Started

Make sure Python 3.8+ is installed  
(Optional) Install `matplotlib` for plotting:
```bash
pip install matplotlib

## Why I Built This
-I build this to help me keep track of my leetcode progress




