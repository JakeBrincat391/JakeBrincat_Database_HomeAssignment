# JakeBrincat_Database_HomeAssignment

I created a cluster on Mongo Atlas which was used to connect to Mongo Compass. Mock data was then added to the schema created on Mongo Compass which was then copied to the cluster. Example of mock data: 
_id 67f1203b6ba885a02da3eaf1
name "hero_sprite"
image "https://example.com/images/hero_sprite.png"
description "Main character sprite"

Developed endpoints in the main.py to ensure that "http://127.0.0.1:8000/docs#/default/upload_sprite_upload_sprite_post" lets people upload any sprites/audio/scores to the database

Developed a get endpoint to let people access the images they uploaded based on its id