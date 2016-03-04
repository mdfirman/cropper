rsync -rva --ignore-existing /media/michael/Engage/data/butterflies/web_scraping/ispot/sightings_in_new_format/* admin@oisin:~/butterflies/data/sightings/
rsync -a /media/michael/Engage/data/butterflies/web_scraping/ispot/butterflies_3_to_10.yaml admin@oisin:~/butterflies/data/
rsync -a /media/michael/Engage/data/butterflies/web_scraping/ispot/butterflies_0_to_20.yaml admin@oisin:~/butterflies/data/
echo "Done, don't forget to run 02_just_keep_butterflies to update the yaml file"
