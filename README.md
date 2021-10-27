# Crossword GUI
The Crossword GUI is a python script to gather the latest crosswords from the New Yorker into a single app. 

CONTENTS
========
* [Why](#why)
* [Setup](#setup)
* [How to run](#how-to-run)
* [How it works](#how-it-works)
* [Things to work on](#things-to-work-on)

## Why
### Background
Over the course of the Covid induced lockdown I became increasingly interested in solving crosswords and almost exclusively the New York Times (NYT) crossword.
During this time of increased interest in crosswords I became aware of some very public and damning criticisms of the NYT crossword (including the [Atlantic](https://www.theatlantic.com/culture/archive/2020/03/fight-to-make-crosswords-more-inclusive/608212/) and [Time](https://time.com/5871704/erik-agard-usatoday-crossword-diversity/) magazines).
I then started searching for other outlets and was drawn to the New Yorker puzzles because of their (subjectively) great puzzle creators.

### No New Yorker Crossword App
I feel a big reason that I got into solving the NYT crossword was because their mobile app made it very easy to access/complete.
Unfortunately at the present time the New Yorker does not have an android app (for either the magazine or crossword). 
My goal is to eventually create a standalone mobile app to solve the New Yorker crosswords on android.
Creating a desktop application in python seemed a reasonable first step, with porting being a future step.


## Setup
NOTE: This project used the excellent [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) for creating and managing the virtual environment. 
virtualenvwrapper is not necessary to run to this project, simply replace `mkvirtualenv` and `workon` below with your chosen way of creating/activating a virtual environment.  

- Clone the repo 
  `$ git clone https://github.com/kevinbeirne1/Crossword-GUI-App.git`
- Create/activate the virtualenv
  `$ mkvirtualenv -a <project_directory> <virtualenv_name>`
- Install the project requirements
  `$ pip install -r requirements.txt`

## How to run
- Activate the virtual environment
  `$ workon <virtualenv_name`
- Run the program
  `$ python crossword_gui/__main__.py`
- Answer yes to search for the latest crosswords
- In the left panel click the crossword you want to do
- Work on the crossword in the right panel

## How it works
The project makes use of the [scrapy](https://docs.scrapy.org/en/latest/) and [PyQt5](https://www.riverbankcomputing.com/static/Docs/PyQt5/) libraries

- On starting the program the user is asked whether to search for the latest crosswords
- If yes: 
  - The spider crawls through the New Yorker crosswords puzzles page to get 
direct links to the crosswords
  - The spider appends any new scraped data to `crossword_data.json`
- If no:
  - The spider doesn't run and proceeds to GUI launch


- The GUI launches displaying two panes
  - The left has a list of crosswords from `crossword_data.json` 
  - The right has an embedded browser for displaying the crossword
- Clicking on a crossword in the left pane loads the corresponding crossword in the
browser window

## Things to work on

### GUI
  - Add tick box to left section (beside each crossword name) to mark completed
  - Make left/right section divider adjustable
  - Add maximize/minimize buttons to control pane

### Other Crossword Formats
  - Generate algorithm to parse .puz files to get clues, answers, grid shape
  - Create a GUI to translate the parsed .puz data to a grid
  - Enable Add functionality to GUI/program to add local files to the library

### Offline Solving
  - Update the scrapy spider to save the new yorker crosswords to a local directory

### Android
  - Generate an APK for the app
  - Run on a VM to check operation
  - Some potential issues that may arise on mobile:
    - Size of libraries required to run: PyQt library is ~350mb on PC
    - Existing New Yorker crossword format not optimised for mobile
    - Sectioned window not suitable for mobile







