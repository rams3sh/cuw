# cuw
CUW or (C)heck for (U)pdates for (W)indows tool

The tool helps a person in assessing the maturity of patching cycle for a system.

The tool maintains a local database consisting of Windows patches and it's details. This databases can be updated through the tool.
Basically , during the update process the tool downloads the official WSUS offline cab file from the link "http://go.microsoft.com/fwlink/?LinkID=74689" and parses the information and feeds onto the local database.

The tool supports exporting of the database to a csv file.

The user can use the csv to filter out the updates applicable for a specific windows product or a system by using filter criteria in 'Title' column of the csv using any spreadsheet viewer tools. Once the user finalises the applicable updates, he/she can copy the updateids of the concerned updates into a text file and then feed the file to the cuw tool. cuw tool will solve the supersede updates and give final output consiting of latest updates applicable for the assessing machine.


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
