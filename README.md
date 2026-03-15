This is an Anti-Piracy system to see if it can Fool the crackers<br/>
The encryption is not the encryption in standard terms but acutal randomization of blocks of the execution file<br/>
As a result the crackers will have an extremely hard time to make sense of the code if we add code obfuscation too<br/>

* The system works by encrypting the working exe file by randomizing its blocks based on a Product Key
* Tested OS: Linux

-- To encrypt

````python3 main.py main.exe -S scrambled.exe -K HE12-43NK-AIDD-N986````

+ main.py has the actual logic
+ main.exe is used to read total lines, total words, total characters, most frequent word and average words per line from sample.txt
+ -S stands for Scramble
+ scrambled.exe is the encrypted result
+ -K stands for Key
+ HE12-43NK-AIDD-N986 is the used key and using different keys will result in different variations

-- To decrypt

````python3 main.py scrambled.exe -R restore.exe -K HE12-43NK-AIDD-N986````

+ scrambled.exe is the encrypted exe file
+ -R stands for Restore
+ restore.exe is the decrypted result
+ -K is for key and HE12-43NK-AIDD-N986 is used as the decryption key

###################################################################################

New Addition (restore.py)

-- To run without decrypting

+ Just-in-Time restoration of the scrambled.exe
+ scrambled.exe can be directly through restore.py which acts as a launcher

````python3 restore.py scrambled.exe````

````Product Key: HE12-43NK-AIDD-N986````

+ The product key must be exactly the same

####################################################################################

Updated Version: Introducing Server Client 

- The server now stores the respective activation key
- For the user to get the activation key they have to send the license key to the server through launcher.py
- The user have to also select the scrambled.exe (Note: It can be any other executable such as .AppImage or .x86_64)
- The server will collect the license key, hash of the scrambled.exe and the user device's fingerprint

  The server currently runs on localhost<br/>
  The server checks the user device's fingerprint and compare it if the fingerprint similarity is low then the user is not validated<br/>
  The corresponding hash and keys to use is stored in licenses.db<br/>
  To licenses can be created and checked using db_creation.py and db_check.py respectively<br/>

To start simply run:

First: ````python3 server.py````
Second: ````python3 launcher.py````
