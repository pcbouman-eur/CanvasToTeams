# Canvas LMS to MS Teams

## Introduction

These are two scripts that can be used to take students that are enrolled in a course on the Canvas LMS and add them to a Team on MS teams and to a private channel based on their section on Canvas.

The main use for this is to create a Team with a private channel for each tutorial group, and registering students based on their registration information on Canvas.

## Requirements

There are two scripts: `get_students.py` which is a Python script that retrieves relevant data from a Canvas course using the Canvas API, and `add-to-teams.ps1` which is a Powershell script that can be used to import the data that was retrieved from Canvas into MS Teams.

To be able to use this, you first need to create a Canvas Access token. You can create a new token for your Canvas account under "Settings" in your Canvas account. You also need to install the Python package `canvasapi` to be able to use this. This can be installed using `pip install canvasapi`.

To be able to use the Powershell script, you need to have a working version of the [Microsoft Teams Powershell Cmdlet](https://docs.microsoft.com/en-us/microsoftteams/teams-powershell-overview) installed. Although Microsoft mentions that there are issues with Powershell 7, I personally was only able to get it to work in Powershell 7. Note that feature to add users to private channels is still in preview, so you need to install the Cmdlet by running the following command in an Powershell environment with Administrator privileges:
```
Install-Module MicrosoftTeams -AllowPrerelease -RequiredVersion "1.1.3-preview"
```

## Using the script

### Retrieving Students registrations from Canvas

First you need to run the `get_students.py` script to download the relevant information as a `.json` file. The two things you need for this are your Canvas Access Token and the Canvas ID of your course (you can see this in the URL when you navigate to a Canvas course). The scripts provides a number of other prompts to automatically transform the data to a format that is nicer to use in MS Teams. You can leave the prompts empty to use the default options.

If the extraction is succesful, you will get a json file with the following structure:
```
{ "Channel 1" : ["userid1", "userid2", "userid3"], "Channel 2" : ["userid1", "userid3", "userid4", "userid5"]}
```
This specifies that three users will be added to a private channel called `Channel 1`, and four users are added to a private channel called `Channel 2`.

**Note:** it is also possible to write your own `.json` file rather than extract the data for Canvas. You can then directly use the powershell script to add the `.json` file to MS Teams.

### Importing the users in MS Teams

Before importing the users into MS Teams, inspect if your `.json` file looks as it should. If it does, you can proceed to import the users into your Team. For this, you need to obtain the *Group ID* of your Team. The way to obtain this is to go to your team, and in the settings of the team click *Get link to team*. This link will contain the groupId as part of it's URL, i.e. `groupId=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`. Copy the groupId (without the `groupId=` part) and paste this into the script's prompt when it asks for the groupId of the team.

You also need to create the private channels before you are able to users to them. **Currently, the script can only add users to channels that already exist. It does not create channels**.

When you have the groupId and the private channels are created, you can run the script. Enter the path to the `.json` file that contains the users you want to import, and provide the groupId when the script asks for it. When importing students, you should leave the prompt whether to add the users as an owner empty as you should not make students owners of the channels. Since sometimes random errors occur, it is a good idea to give a filename to which errors can be written.

After you have provided relevant configuration to the script, the script need to log in to MS Teams. It will show a message in yellow pointing to `https://microsoft.com/devicelogin` and showing a code. Go to this URL in your browser, copy and paste the code shown and select the account which you want to use to perform the addition of users to the teams and channels. The account you use for this should be an owner of the team or have some other type of administrative rights before this works. When you complete the login process in the browser, the script should start adding users to the teams and channels.

After all users are imported, it is probably a good idea to check this error file and try to add the students where the script failed manually.