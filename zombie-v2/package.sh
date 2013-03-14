cd ..
zipname=ZombieGame-v2.4.zip
echo Creating new package $zipname in parent directory
rm $zipname
zip -r $zipname zombie-v2/readme.txt zombie-v2/ZombieAssignment.txt zombie-v2/*.py
