Author: Vedran Furtula
Date: 28 Sept 2019

Welcome to the PLD instrument control software python code. This code is used to control communucation between a PLD photon source, a Thorlabs detector diode and a host computer.

####################################################
################### RUN THE CODE ###################
####################################################

In order to run the program in Windows type use the Anaconda prompt:
python Run_GUI.py

In order to run the program in Linux type:
python3 Run_GUI.py

The folder named "Data" contains collected/measured data from the PLD setup. If you have any new measured sets of data please put those files in this folder. However, you can store your post processed data anywhere by filling in the location in the "Create folder/file" edit field on the bottom of the GUI, ie. if the folder entered in this field is not existing it will be created for you.

############################################
################### HELP ###################
############################################

All the individual functions/steps shown in the GUI are explained in the help menu found on the main bar.

#####################################################
################ INSTALL FOR WINDOWS ################
#####################################################

To run the code in Windows install Anaconda for Python 3:
https://www.anaconda.com/distribution/

###################################################
################ INSTALL FOR LINUX ################
###################################################

To run the code in Linux first make sure that you have Python 3 is installed:
https://docs.python-guide.org/starting/install3/linux/

For Linux users, make sure to install all the necessary Python modules such as numpy, matplotlib, scipy, yagmail using "pip3 install [module]".
