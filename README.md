# Sensei (HackMIT 2015)

##Team
- Piyali Mukherjee
- Anshul Gupta
- Jackie Luo
- Annie Zhang

##Algorithm Design
Currently, we support a MATLAB desktop application which takes in a video file (.mp4) as input. 
We first create a foreground and background separator using MATLAB's ForegroundDetector. Then, we establish Kalman filters to track the moving objects in the foreground using photometric distortions. Finally, we render the input video and the output grayscale along parallel video players for users to see the results of the videos. 

[![Sensei in action](https://j.gifs.com/m2GGMJ.gif)](https://www.youtube.com/watch?v=bkN14S4BR5U)

Sensei placed in the top three at HackMIT and won GE's Most Innovative Use of Data award. The project was featured in [Bwog](http://bwog.com/2015/09/25/columbia-team-places-third-at-hackmit/), Columbia's student-run news website.
