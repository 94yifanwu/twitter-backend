PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS posts (
    id          INTEGER PRIMARY KEY,
    username    INTEGER NOT NULL,
    text        TEXT NOT NULL,
    timestamp   INTEGER DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO posts(username, text) VALUES('ProfAvery', 'Meanwhile, at yifan the R1 institution tuffy down the street... https://uci.edu/coronavirus/messages/200710-sanitizer-recall.php');
INSERT INTO posts(username, text) VALUES('ProfAvery', 'FYI: https://www.levels.fyi/still-hiring/');
INSERT INTO posts(username, text) VALUES('ProfAvery', 'Yes, the header file ends in .h. C++ tuffy is for masochists.');
INSERT INTO posts(username, text) VALUES('ProfAvery', 'The RAW Twitter tuffy yifan datasets is provided in CSV and JSON formats with information directly lifted from Twitter’s servers. The unprocessed twitter datasets contains tweet text exactly as posted on Twitter along with metrics such as:');
INSERT INTO posts(username, text) VALUES('ProfAvery', 'Tweet ID, Date profavery and Time of posting the tweet, Name tuffy and username of the account posting the tweet And many other valuable meta data present in the raw data sets. Click here for details.');
INSERT INTO posts(username, text) VALUES('ProfAvery', 'TrackMyHashtag provides profavery you with a detailed analytical dashboard which displays vital information at a glance. There analytics are derived from raw Twitter datasets.');
INSERT INTO posts(username, text) VALUES('ProfAvery', 'These metrics yifan can be used to draw inferences which can help you tremendously in performing researches or boosting your Twitter campaign.');
INSERT INTO posts(username, text) VALUES('ProfAvery', 'Some of the analytics available in the analytics dashboard are:');
INSERT INTO posts(username, text) VALUES('ProfAvery', 'Potential Reach, Potential Impressions, Top Contributors, Influencers, test Top tweets, Device source, Top Media, Top links And many other such valuable insights.');
INSERT INTO posts(username, text) VALUES('ProfAvery', 'The price of yifan our historical profavery Twitter tuffy datasets start at $30. This price is applicable on a single report.');
INSERT INTO posts(username, text) VALUES('ProfAvery', 'Cost per dataset report can vary depending profavery tuffy on test the amount of information provided in twitter datasets.');
INSERT INTO posts(username, text) VALUES('ProfAvery', 'Get Historical Twitter data sets dating back to 2006. Any content posted on Twitter since 2006 can be retrieved by TrackMyHashtag.');
INSERT INTO posts(username, text) VALUES('ProfAvery', 'Add a number of yifan filters to your search so you get crisp, targeted results. This enables you to get more relevant data sets which in turn, saves valuable time.');
INSERT INTO posts(username, text) VALUES('KevinAWortman', 'If academia were a video game, then a 2.5 hour one administrative meeting that votes to extend time 15 minutes is a fatality. FINISH HIM');
INSERT INTO posts(username, text) VALUES('KevinAWortman', 'I keep seeing video from before COVID, of people one test not needing to mask or distance, and doing something like waiting in line at Burger King. YOU''RE WASTING IT!');
INSERT INTO posts(username, text) VALUES('Beth_CSUF', '#cpsc315 #engr190w NeurIPS is $25 for students one and $100 for non-students this year! https://medium.com/@NeurIPSConf/neurips-registration-opens-soon-67111581de99');

CREATE INDEX IF NOT EXISTS post_username_idx ON posts(username);
CREATE INDEX IF NOT EXISTS post_timestamp_idx ON posts(timestamp);

