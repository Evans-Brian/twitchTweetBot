## Twitch Watch Time Twitter Bot

I created a <a href="https://twitter.com/TwitchWatchTime" target="_blank">Twitter bot</a> that tweets daily watch time in hours for a variety of games and streamers. The bot will tweet yesterday's total watch time in hours for the top 5 streamers, games, and top 5 streamers of a random game. Twitter users may also query the data by tagging the bot (@TwitchWatchTime) in a Tweet containing a game or streamer name. The bot runs on a t2.micro EC2 instance.  It's containerized with Docker, so collaborators may easily run the bot on their own.  

You can see the bot in action <a href="https://twitter.com/TwitchWatchTime" target="_blank">here</a>.

#### Data Sourcing and Storage
Every 30 minutes script requests data from the <a href="https://www.google.com/" target="_blank">Twitch API</a> on viewer count and game name for all streamers who have over 50 viewers. After pulling the data, the script writes it to a series of staging tables in the PSQL database. Functions for reading and writing data from the Twitch API may be found in *helperfunctions/twitchAPI.py* and *helperfunctions/updateTables.py*.

#### Sending Tweets
Each day at 8AM PTC, the bot will write the data stored in the staging tables to a series of permenant tables containing data for the past 24 hours. Because Twitch is a global platform, there is no defined start and end of each day. I analyzed Twitch viewership and learned it bottoms out each day at around 8AM PTC, which is why I determined each day will end at 8AM. Functions for writing data to the permenant tables may be found in *helperfunctions/updateTables.py*. 

Each day at 2PM PTC, the bot will tweet out the yesterday's viewing hours top 5 games, streamers, and top 5 streamers for a random game. View time is estimated and likely to be slightly high- because we pull data every 30 minutes, each view represents 30 minutes of view time. The random game tweeted is weighted on total game view time.
image
image
image

Additionally, users may tag the bot in a Tweet containing a game name or streamer name. If the name is found in the database, the bot will respond to that user with the top 5 streamers for that game or the top 5 games for that streamer.
image


## Installation and Setup Instructions

#### Example:  

Because I've containerized this app using Docker, users may easily run it within the project's container. 

To install Docker:

`sudo yum update -y`  
`sudo yum install docker -y` 

To start Docker:

`sudo service docker start`  

To compose the container, built from a Postgres image and Ubuntu image:

`docker-compose up`  

This app contains many API keys and secrets. To store these credentials safely, I used AWS Secrets Manager. Users will need to update API credential references. If they wish to use AWS Secrets Manager, they need to update the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables found in the Dockerfiles. 

## Reflection

I created this side project to explore technologies that I had minimal experience working with:
1. EC2
2. Docker
3. APIs
4. Database integration

### EC2
I had no experience hosting a project on EC2, but it was clearly the optimal solution for this use case. Because this bot runs 24/7, using my personal computer was not feasible. I deliberated over what instance size to use, but decided to go with AWS's limited free use t2.micro instance. The compute power required for the bot is minimal, but more storage would be useful for allowing users to query the bot for time periods beyond 1 day. I could've also used AWS's RDS service for my database, but decided this was beyon the scope of the project.

Beyond storage space, the t2.micro compute power became an issue when SSHing in through VS Code and while performing code changes when testing. Spikes in compute would often use all my CPU credits, leading to a crash. I found the quickest way to restore the SSH connection was to reboot the instance.

I used AWS Secrets Manager to store credntials. I've used many different tools for credentials storage, but found Secrets Manager useful for it's ability to share credentials across different AWS services.

### EC2

### EC2

### EC2

#### Example:  

This was a 3 week long project built during my third module at Turing School of Software and Design. Project goals included using technologies learned up until this point and familiarizing myself with documentation for new features.  

Originally I wanted to build an application that allowed users to pull data from the Twitter API based on what they were interested in, such as 'most tagged users'. I started this process by using the `create-react-app` boilerplate, then adding `react-router-4.0` and `redux`.  

One of the main challenges I ran into was Authentication. This lead me to spend a few days on a research spike into OAuth, Auth0, and two-factor authentication using Firebase or other third parties. Due to project time constraints, I had to table authentication and focus more on data visualization from parts of the API that weren't restricted to authenticated users.

At the end of the day, the technologies implemented in this project are React, React-Router 4.0, Redux, LoDash, D3, and a significant amount of VanillaJS, JSX, and CSS. I chose to use the `create-react-app` boilerplate to minimize initial setup and invest more time in diving into weird technological rabbit holes. In the next iteration I plan on handrolling a `webpack.config.js` file to more fully understand the build process.