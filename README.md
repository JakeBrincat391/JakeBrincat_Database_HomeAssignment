# JakeBrincat_Database_HomeAssignment

Task 1: Setting up the evironment

Step 1: Create a new terminal in Visual Studio Code

Step 2: Input the following commands:
        - py -m venv env
        - Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
        - env/Scripts/activate

Step 3: Install the dependencies in the VS Code terminal (check that you are in the environment by checking for (env) before the command)
        using the following command:
        - pip install -r reqiurements.txt


Task 2:

I created a cluster on Mongo Atlas which was used to connect to Mongo Compass. Mock data was then added to the schema created on Mongo Compass which was then copied to the cluster. Example of mock data: 
_id 67f1203b6ba885a02da3eaf1
name "hero_sprite"
image "https://example.com/images/hero_sprite.png"
description "Main character sprite"


Task 3:

Developed endpoints in the main.py to ensure that "http://127.0.0.1:8000/docs#/default/upload_sprite_upload_sprite_post" lets people upload any sprites/audio/scores to the database

Developed a get endpoint to let people access the images they uploaded based on its id

The endpoints were tested to ensure that they were working correctly. The files given were uploaded correctly and given ID's. The ID's were then used to test if the get endpoint was working. The ID was given and the database gave the image uploaded, back as a picture with its properties.
I did the same process for the audio files and the player scores.

The API was then tested using postman. Screenshots were taken and put into the documentation of how postman was setup to upload files. The files entered in postman were then shown in the database's and could be accessed in the get endpoints.

The database was then deployed using vercel.


Task 4:

Secure credentials on Mongo Atlas were given to the database ensuring that only certain people can access/edit the database. A screenshot of the users was taken and put into the documentation.

Certain IP addresses were whitelisted to ensure that only certain users from certain devices could access it. A screenshot of the IP addresses was taken and put into the documentation.

A code snippet was added to the main.py to prevent SQL injection attacks to the databases. A screenshot of the code snippet was taken and put into the documentation.