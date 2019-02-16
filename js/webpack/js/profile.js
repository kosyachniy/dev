require('style-loader!css-loader!../css/main.css');

var timeline = require('./timeline.js');
var user = {
  name : "Shekhar Gulati",
  messages : [
    "hello",
    "bye",
    "good night"
  ]
};

var timelineModule = new timeline(user);
timelineModule.setHeader(user);
timelineModule.setTimeline(user);