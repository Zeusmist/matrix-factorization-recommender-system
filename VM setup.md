VM setup

Create and Use a Shared Group:

Create a group: `sudo groupadd sharedgroup`
Add users to the group: `sudo usermod -a -G sharedgroup username`
Create the Shared Directory: `sudo mkdir /path/to/shared_directory`
Change the group ownership of the directory: `sudo chgrp sharedgroup /path/to/shared_directory`
Set appropriate permissions for the group: `sudo chmod 2770 /path/to/shared_directory`