# cuw
CUW or (C)heck for (U)pdates for (W)indows tool

CUW helps in assessing the maturity of patching cycle for a system.

Background about CUW
-------------------------

Major inspiration for creation of this tool was to check out the vulnerabilities (in case of a pentest, to find applicable exploits for post exploitation phase) in the existing system and to determine the patch life cycle maturity ( i.e missing patches, same logic as pentest but different view :P ) in case of a compliance audit.

Since determining if all required patches have been applied in the system is a trival task as there is no online one-stop efficient searchable database (post April 2017 because of discontinuation of periodic release of MS Bulletin Excel file)  where patches, its's subsequent superseded patches, patch description etc for a specific product can be searched out and compared with the list of patches installed in the system (if any); and further more to add to the problem is solving manually the logic of superseded patches. Hence the motivation to build this tool.

Working of/with CUW
-------------------

CUW maintains a local sqlite database consisting of Windows patches and it's details.During the update process the tool downloads the official WSUS offline cab file from the link "http://go.microsoft.com/fwlink/?LinkID=74689" and parses the required information and feeds onto the local database. You can consider it as a localised repository of https://www.catalog.update.microsoft.com/Home.aspx but with more filter search capability as the entire data is in your control.

CUW exports a csv format file "MSPatches.csv" containing only important columns from the database table as soon the database is updated.
Note : Raw database is in sqlite format. If you want to view the table in the database, you can use any sqlite viewer tool.

Now the user can use this csv to filter out the the updates containing keyword pertaining to the target operating system or the product installed using his/her super excel powers. The problem doesnt end there as the updates which have been filtered may have superseded updates. So to solve this , the user copies the updateids from the csv file after filtering out the keywords from the file into a text file.
Now this text file is fed into the cuw tool using the "scan" option. CUW takes in the updateids, check for superseded patches within the database and after applying internal logic, gives out the final applicable patch ids which is supposed to be present in the system. Now this output can be used to compare the existing patches and determine the missing patches / vulnerabilities in the target system.

Q) Cant this entire thing of user selecting the required patches and feeding to CUW be automated ?

It can be, provided Microsoft follows a standard and accurate convention of naming its products and the products appicable to each of the updates in the wsusscn2.cab file (The official offline patch database released by microsoft every month to be used with WSUS and WUA tools), since CUW totally depends on the textual search. WSUS , WUA uses a set of detection mechanisms mentioned in the same cab file to determine all the products installed in a workstation and accordingly picks the required updates and patches the system and that is the reason why your regular system takes so much time to update and this entire process is active wheras CUW tries to attempt this very same process passively taking out the installation of patches.

Challenge Explanation :-

To understand the challenge in entirety, the entire cab file structure and its working needs to be explained . Btw there is no official detailed manual explaining the structure of wssuscn2.cab file which I could find apart from this link https://support.microsoft.com/en-us/help/927745/detailed-information-for-developers-who-use-the-windows-update-offline , which at least I couldnt find of any help since I was not using WUA API and I had to understand the entire cab file structure and the internal xmls and its tags to write a tool to parse its contents. I  will save the explanation on how I understood the structure of wssuscn2.cab file for another post in my blog at https://rams3sh.blogspot.com/.

Now to keep it simple and to understand the challenge, lets understand that wssuscn2.cab file stores lot of informations such as Windows Products, Windows Updates, Different ways to check for an existence of a product (Detectoids), types of updates, EULA files, download links for various updates etc in different xml files (not one). Each of these information is mapped to unique ID called updateid (even though many of them are not updates, Microsoft chooses to call it that way). 

So if one wants to look for patches applicable for MS Office 2016, one needs to first search for updateid of the product , search across all the updates where prerequistes column of that update has MS Office 2016's updateid part of it. This can be automated provided the input file,say which consists of list of installed applications' name (received as output from the commmand "wmic product get name") follows the same naming convention as the one in the wsusscn2.cab. But it isnt that way. Look at the example

Example:-

Installed Application: Microsoft Office Professional Plus 2016


WSUSSCN2.CAB Equivalent Product Name: Office 2016

Simple search for existence for 2016 and Office is not enough as there are other examples such as MSSQL 2008 R2 Server as product and installed application is just MSSQL 2008 Client. Hence word matching logic does not work. 

Tried for fuzzy string match logic, still identifying and fixing a threshold ratio for string match was difficult and was not consistent throughout.Hence left the challenge of selecting the updates to the user.

If you have any solution for this, you can let me know at my mail id godzillagenx@gmail.com (dont judge me by my emailid:P)

If this challenge is overcome, the process of update selection by the user can be automated.



Q) Is there any possibility of inaccuracies on the output of results ?

Yes, if the update ids of the applicable updates (after filtration process in csv) provided by the user to the tool is inaccurate as the tool is merely solving the superseded update logic.


Some of the Key Information required for the user to filter the required updateids before using the tool
--------------------------------------------------------------------------------------------------------

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
        
  
External Dependency
-------------------
 
 cuw depends on 7zip binary. 
 The required binaries has been packed along with the release zip file. The author claims no ownership over the same.
 
Note
----
If you are using the source cuw.py, then you would have to dowload 7z binaries (7z.exe and 7z.dll) separately from the official site and place it in class path and update the entire database. The initial updation on my machine which is i7 7th gen with 8GB Ram and Win10 OS took 3 hours of time.
 
The release zip has been also packed with latest updated database and csv file as on 17-6-2018 to avoid long update process.


Future Plans
-------------

To add exploitdb informations to the database so that a mapping exploit (if any) also could be given out along with the report. More or less like windows_privesc_check (https://github.com/pentestmonkey/windows-privesc-check/blob/master/docs/MissingSecurityPatchesVsPublicExploits.md) just that I wouldnt want to limit to priv escalation related exploit alone.



