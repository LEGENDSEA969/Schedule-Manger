# Schedule-Manager
#### Video Demo:  <https://youtu.be/TtGvFjUmTIM>

#### Description:
## What It Actually Does
You download the app, open it, and click “Choose Your Schedule File.” You pick the PDF your university gave you. Behind the scenes, the app reads the PDF’s structure, pulls out the course codes, names, times, rooms, and even your student info. In a few seconds, your schedule appears—not as text, but as a color-coded weekly calendar.
The main view is a table. The columns are the days (Sunday to Thursday, which is the standard week at my university). The rows are time slots, from 7:00 AM to 9:30 PM. Each class is a colored block placed in its correct time slot, showing the course name and room. It’s instantly obvious when you have class, when you’re free, and where you need to be.
Want more details? Click the information button on any class block. A window pops up with everything the PDF contained: the exact course code, the instructor’s name, how many credits it is, and the activity type (lecture, lab, etc.). All the info is there, just organized and accessible.
The app remembers the last file you opened. Next time you launch it, your schedule loads right back up. The interface uses a dark theme to be easier on the eyes during late-night study sessions.

## The Problem It Solves
Every academic term, students are handed schedules in formats that are inconvenient and confusing. Colleges and universities often distribute PDFs filled with ambiguous headings like “Period 1” or “Period 15,” and rarely provide a clear, visual layout that shows exactly when each class takes place. When you try to copy this information, the formatting collapses—lines mix together, spacing disappears, and what should be a simple timetable turns into a tangled mess that’s nearly impossible to decipher. If you’re trying to plan your week or ensure you’re in the right place at the right time, you’ll likely end up rewriting everything by hand, spending hours just to create a usable schedule. Mistakes are easy to make, and the process is tedious, adding unnecessary stress to an already busy semester.
It’s not just about clarity—it’s about usability. A jumbled schedule makes it hard to spot overlaps, free periods, or consistent routines. You might miss a lab session because it was buried in a paragraph or show up to the wrong room because the location was listed in a separate, unaligned column. These small errors waste time, create anxiety, and pull your focus away from your studies. And if you’re someone who likes to color-code, add reminders, or share your timetable with peers, the manual reformatting becomes a multi-step nightmare involving spreadsheets, highlighting, and constant tweaking.

## How It Works
At its core, the app is a Python program with a GUI built using PySide6. The heavy lifting is done by a library called pdfplumber, which can “read” the tables inside a PDF. The code I wrote looks for specific patterns in those tables—it finds rows that contain course codes, extracts the relevant columns (course name, time periods per day, location, etc.), and then maps those period numbers (like “7” or “12”) to real time slots in the app’s interface.
The most fiddly part was getting the data extraction to work reliably, because not every PDF is perfectly structured. The code has a lot of safety checks (try...except blocks, as we call them) to handle missing data gracefully so the app doesn’t crash if a PDF is slightly off.
The UI is fairly straightforward: a set of labels at the top for your student info, the big table in the middle, and a button to load a new PDF. The “magic” is in taking the raw, extracted data and placing it correctly in that table, complete with distinct colors for each course.

## The Result
Now, at the start of the semester, I just open the app and load my PDF. I have my entire schedule—clear, visual, and interactive—in under a minute. I can quickly see that I have a free afternoon on Tuesday, or that my Wednesday starts with back-to-back classes in different buildings. It has eliminated that small, specific stressor of schedule management for me.
The goal was never to build a massive, feature-packed project management tool. It was to solve one annoying problem well: making my university schedule actually readable. And that’s exactly what it does.
