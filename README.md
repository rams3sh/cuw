# cuw
CUW or (C)heck for (U)pdates for (W)indows tool

The tool helps a person in assessing the maturity of patching cycle for a system.

The tool maintains a local database consisting of Windows patches and it's details. This databases can be updated through the tool.
Basically , during the update process the tool downloads the official WSUS offline cab file from the link "http://go.microsoft.com/fwlink/?LinkID=74689" and parses the information and feeds onto the local database.

The tool supports exporting of the database to a csv file.

The user can use the csv to filter out the updates applicable for a specific windows product or a system by using filter criteria in 'Title' column of the csv using any spreadsheet viewer tools. Once the user finalises the applicable updates, he/she can copy the updateids of the concerned updates into a text file and then feed the file to the cuw tool. cuw tool will solve the supersede updates and give final output consiting of latest updates applicable for the assessing machine.

What to get from the machine (that is to be assessed) before using the tool
-----------------------------------------------------------------

1. System Information 
To get the operating system details, architecture and other informations.

Command : systeminfo.exe

2. Build Version of the Operating System
This helps in filtering out the updates further from a set of updates applicable for an operating system.

Example :-
Both of the following updates apply for Windows 10 but each one for different Version of Windows 10
i. 2018-06 Cumulative Update for Windows 10 Version 1709 for x64-based Systems
ii. 2018-06 Cumulative Update for Windows 10 Version 1803 for x64-based Systems
So differentiating factor is the Version Number here.
  
Command :reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v ReleaseId

3. Get List of Installed Programs 
This will help us in finding the list of programs installed in the machine. The program names can be used to filter out the applicable updates from the csv file.

Command : wmic product get name,version,vendor,installdate

4. Get list of updates installed in the system 
This will help us to compare the output from the tool and the installed updates to decide on which updates are missing in the system (if any).

Command : wmic qfe list
     
Note: None of the commands or outputs given by the commands mentioned above are used by the tool. These details are just for the user to finally filter out the required updates from the MSPatch csv file.


How To use
-----------

Usage:-
                

    cuw.exe scan <filename with updateids> - Checks for Update ids in the input file and gives the final list of applicable updates with details
    cuw.exe scan <filename with updateids> output <output file name> - Same as the previous option with the output (with extra details) being exported as csv
    cuw.exe update - Updates the local patch database (Requires Internet Connection and some patience !! :P)
    cuw.exe exportdb <filename of the exported csv>" - Exports the local patch database as csv file
    cuw.exe help  -  Displays this help
        
  
 Dependency
 ----------
 
 cuw depends on 7zip binary. 
 The required binaries has been packed along with the release zip file. The author claims no ownership over the same.
