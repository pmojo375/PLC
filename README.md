<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <h3 align="center">PLC Read/Write</h3>
  <p align="center">A simple command line script to read and write to Allen Bradley PLCs.</p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project

This project came about after realizing there were no decent ways to read and
write PLC tags programmably. With python being my preferred language of choice,
I set out to find if there were any options already out there and discovered the
Pycomm3 library which had the ability to easily read and write PLC tags on the
Allen Bradley PLC line. After writing custom scripts for all my use cases, I
figured I should just write up a CLI wrapper to handle that for me. I also
wanted to share the functionality with anyone who might not be comfortable with
the writing their own code to utilize the library.

#### Features include:

* Read a single PLC tag
* Write a single PLC tag
* Read multiple PLC tags from a CSV file
* Write multiple PLC tags from a CSV file and output their results to another CSV file
* Trend a single PLC tag and store the timestampped results to a CSV file
* Trend multiple PLC tags and store their results to a CSV file


### Built With

* [Python](https://python.org)


<!-- GETTING STARTED -->
## Getting Started

Currently you may start the script from python in the CLI with a GUI planned for the future. Before you start though, you will need to install the nessesary libraies needed to run the script and, although not technically needed, a virtual python environment is highly reccomended.

All commands should be run with admin privilages and in the project folder and since Allen Bradley PLCs are programmed in Windows, it is assumed that you are using either PowerShell or CMD

### Prerequisites

* Virtual Environment (optional but reccomended)
  ```sh
  python -m venv ./venv
  ```
* Python 3.x

### Installation

1. If you installed the virtual environment, enable it.
  ```sh
  ./venv/Scripts/Activate.PS1
  ```
2. Install the python libraries from the requirements.txt file.
  ```sh
  python -m pip install -r requirements.txt
  ```
3. Change the settings in the config.yaml file as needed for your application (see below for details)
4. If reading/trending or writing multiple tags populate your CSV file with the tag names and values if writing (see below for details)
5. Run the script!
  ```sh
  python plc.py
  ```
6. Hopefully not break anything...



<!-- USAGE EXAMPLES -->
## Usage

#### Config.yaml parameters:
* DEBUG - Used to test the script without any PLC connection being needed. Can be used to verify the CSV files are formatted correctly.
  - Only accept 'True' or 'False'
* IP - Set the IP address of your PLC. IF your PLC is a ControlLogix and is NOT in the first slot, you may designate the slot number by appending a '/#' after the IP address.
  - If this is removed from the config file, the script will prompt you for the IP address (and slot if applicable)
* STREAMFREQ - Sets the rate in seconds that the trend functions capture data. I have not verified the accuracy of the actual reads yet but they should be near the timestamps outputted and close to this rate.
* OUTPUT - The output file name for your generated CSV files. The '.csv' is appended in code.
* DEFAULT_INPUT - Set to True or False to indicate if the script should prompt you for the CSV file to read or use the default name (set in the next parameter).
* INPUT - The default CSV file to read. Only used if the DEFAULT_INPUT parameter is set to True. the '.csv' is appended in code.

#### CSV Structure
* Example files included to test the script in debug mode if you desire.
* All CSV files must have a header of 'tag' and if you're writing tags, 'value'. Including the 'value' in files that are used to only read tags will not hurt anything. As long as it has a 'tag' column it should work.
* Outputted CSV files vary depending on what function you are running.
  - If simply reading tags, they will contain a column for the tag name, again called 'tag', and a column for the read value called 'value'.
  - If trending tags, there will be a timestamp column, and then a column title by the tag name for each tag being trended. If the tags being trended are UDTs, the script will break out the UDT into its full name and use that for the column name.
    - For example, if you want to read a UDT with multiple layers, your column names will be 'UDT_Tag_Name.Nested_Tag_Name.2nd_Nested_Tag_Name' for each tag in the UDT.


<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/pmojo375/PLC/issues) for a list of proposed features (and known issues).

### Features planned
* Reading UDTs when doing a multiple tag read
* A GUI for those who prefer that over the CLI
* General improvements that I am too lazy to fix now
* Ability to output tags in their own seperate CSV files
* Ability to trigger trends to start after other conditions are met
* Output plots of the trended data
* More use of the pycomm3 library's features



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

I am new to Github/Git and really anything more than simple python scripts and also am a budy man so I may not be able to review any pull requests in a timely manner. Please bare with me in that regard.



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Parker Mojsiejenko - pmojo375@gmail.com

Project Link: [https://github.com/pmojo375/PLC](https://github.com/pmojo375/PLC)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [pycomm3](https://github.com/ottowayi/pycomm3)
