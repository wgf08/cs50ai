To find out what was optimum for me I did the following:
    I first tried diefferent amounts of dropout layers, whereby I found that exceeding 0.2 dropout generally began to make the AI have a loweer peak performance , and take longer to train.
    I tried placing it in different locations and decided that the best place for the dropout layer to go was at the end, as the end layer was effected by all layers before it, so we are not overly relying on any part of the network that comes before it.
    I added conv2d layers until performance dropped and thought a 5x5 was a good start as a picked out general details, followed by a 2x2 to pick up finer details
    One thing that didnt work too well at all was adding too many max pool layers, I assumme as when you shrink an image enough, you begin to lose information. i STUCK TO ONE OR TWO
    I tried MinPooling following MaxPooling, but this had a little yet negative effect!
    I managed to reach performance of around 95%, the majority of the time, performance reaches around 90% - 91%.
    I changed the number of epochs to 7 as I believe this is the point where change in loss fluctuates, so it is pointless to continue
    I noticed using tanh instead of relu lead to a SEVERE and RAPID increase in accuracy, so I used it instead
    THANK YOU VERY MUCH FOR READING

