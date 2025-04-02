# Student Data Processing Script

## Overview

This project processes student data from an Excel file (`students.xls`), retrieves corresponding student photos from Google Drive, and applies transformations to these images. The script:

- Reads student information from an Excel file.
- Maps student data to a predefined structure.
- Fetches student photos from Google Drive based on a naming convention.
- Processes each image and removes temporary files after processing.

## Prerequisites

Before running the script, ensure you have the following setup:

1. **Create a Google Cloud Project & Enable Drive API**

   - Follow the [Google Drive API Quickstart](https://developers.google.com/workspace/drive/api/quickstart/python).
   - Download `credentials.json` and place it in the project directory.

2. **Prepare the Student Data File (`students.xls`)**

   - Ensure the file is in the project directory.
   - The file should contain the following columns:

     | Last Name | First Name | Middle Name | Login | Canvas | ID  |
     | --------- | ---------- | ----------- | ----- | ------ | --- |
     | Doe       | John       | Smith       | 12345 | jdoe   | 001 |
     | Roe       | Jane       | Adams       | 67890 | jroe   | 002 |

3. **Grant Access to Google Drive**
   - The Google Drive account used must have access to the student photos.
   - The photos should be stored in a folder accessible by the project.
   - Each photo must follow the naming convention: `FIRSTNAME LASTNAME MIDDLENAME.jpg` (e.g., `John Doe Smith.jpg`).

## Installation

Install the required dependencies:

```sh
poetry install --no-root
```

## Running the Script

Execute the script with:

```sh
poetry run python script.py
```

## Notes

- The script will fetch student photos, process them temporarily, and delete them afterward.
- Ensure that `credentials.json` is correctly set up to authenticate with Google Drive.
- If a student photo is missing or incorrectly named, it will not be processed.
