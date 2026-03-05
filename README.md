#  LeetTracker

The program is no longer just a CLI tool but are basic web application that stores leetcode problem feedback

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
  - Cleanly display information obtained from user.
---

##  Folder Structure
```text
LeetTracker/
├── main.py             # CLI
├── app.py              # Web app (Flask)
├── problem_tracker.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
├── utils/
│   ├── storage.py
│   ├── time_parse.py
│   └── plot.py         # (Will be added soon for plotting feature)
├── data/
│   └── problems.json
```
---

##  How to Run

### CLI
1. Open a terminal in the project directory
2. Run: `python main.py`
3. Use the numbered CLI menu to add problems, append notes, and view stats

### Web App
1. Install dependencies: `pip install -r requirements.txt`
2. Run: `python app.py`
3. Open http://127.0.0.1:5000 in your browser

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
- Use webextension/API or something of that nature to collect info directly from leetcode page(time spent, and problem info)
- Visualize performance with `matplotlib`
- Add spaced repetition or revisit tracking
- Export to CSV or Markdown for publishing
- Polish webpage and prompt for info from user but make more of the prompts optional
---


```
## Why I Built This
-I originally built the CLI to help moniter leetcode progress and brush up my python skills because i hadn't used it in a while. I've been planning to create a front end in the form of a GUI or webpage to make it more resume appropriate. I implemented a very basic webpage using Flask, HTML, and CSS.
