# :rabbit: Bunnybook :rabbit:

## A tiny social network (for bunnies), built with FastAPI and React+RxJs.

## [Click here for live demo!](http://137.184.46.182)

<kbd>
  <img src="https://user-images.githubusercontent.com/19171248/131324206-1f97c51b-7192-4e62-8619-abde46aea5b6.png"/>
</kbd>

<div>&nbsp;</div>

Included features:
- :speech_balloon: chat
- :red_circle: online/offline friends status
- :abcd: "Is typing..." indicator
- :two_men_holding_hands: friend requests and suggestions
- :bell: notifications
- :postbox: posts
- :pencil: comments
- :scroll: conversations history
- :rabbit2: random profile picture generation
- :lock: authentication

Tech stack:
- :snake: Python 3.8 + FastAPI
- :notebook_with_decorative_cover: PostgreSQL 13 + async SQLAlchemy (Core) + asyncpg driver
- :link: Neo4j graph db for relationships between users and fast queries
- :dart: Redis for caching and Pub/Sub
- :zap: Socket.IO for chat and notifications
- :key: Jwt + refresh tokens rotation for authentication
- :whale: Docker + docker-compose to ease deployment and development  

<br/>
Feel free to contact me on LinkedIn for ideas, discussions and opportunities :slightly_smiling_face: https://www.linkedin.com/in/pietro-bassi/ 

## Scope of the project
**What Bunnybook is**: I created Bunnybook to have the opportunity to experiment with some technologies I wasn't familiar with (e.g. Neo4j). I love learning new ways to solve problems at scale and a small social network seemed a very good candidate to test a few interesting libraries and techniques.  
<br/>
**What Bunnybook isn't**: a production-ready social network with infinite scaling capabilities. Building a "production-ready social network" would require way more testing and refinement (e.g. some features scale while others don't, test coverage is not complete, chat is hidden in mobile-mode and the entire project is not particularly responsive etc.), but this is out of the scope of this small experiment.


## Quick start
#### Requirements
- OS: Linux, macOS, Windows 
- Install Docker (https://docs.docker.com/install/)
- (Linux only) Install docker-compose (https://docs.docker.com/compose/install/)
#### Deploy Bunnybook on your local machine
Open a shell and clone this repository:  
`git clone https://github.com/pietrobassi/bunnybook.git`  

Navigate inside project root folder:  
`cd bunnybook`  

Start all services:  
`docker-compose up`  

After some time (first execution might be slow), open Chrome or Firefox and navigate to:  
http://localhost  
<br/>
API documentation is hosted at:
http://localhost:8000/docs and http://localhost:8000/redoc
> Please note: after pulling new changes from this repo, remember to execute `docker-compose up --build` to recreate containers

## Developing
#### Requirements
- OS: Linux, macOS
- Install Docker (https://docs.docker.com/install/)
- (Linux only) Install docker-compose (https://docs.docker.com/compose/install/)
- Install Node v10.16.0 https://nodejs.org/en/, preferably using Nvm (https://github.com/nvm-sh/nvm)
- Install Python 3.8 (https://www.python.org/downloads/), preferably using pyenv (https://github.com/pyenv/pyenv)
- Install virtualenv (https://virtualenv.pypa.io/en/latest/)
#### Development setup
- Clone this repository, navigate inside root folder and execute `docker-compose -f docker-compose-dev.yml up` to start services (PostgreSQL, Neo4j, Redis, etc.)
> If you have other services running on your machine, port collisions are possibile: check docker-compose-dev.yml to see which ports are shared with host machine
- Navigate to "backend" folder and create a Python 3.8 virtual environment; activate it, execute `pip install -r requirements.txt`, run `python init_db.py` (to generate databases schemas and constraints) and then `python main.py` (backend default port: 8000)
- Navigate to "frontend" folder and install npm packages with `npm install`; start React development server with `npm start` (frontend default port: 3000)

Navigate to:
http://localhost:3000

#### Testing
To run integration tests, navigate to "backend" folder, activate virtualenv and execute:  
`pytest`  
This command brings up a new clean docker-compose environment (with services mapped on different ports so they don't collide with the ones declared inside docker-compose-dev.yml), executes integration tests and performs services teardown.
> To execute faster tests during development phase without leveraging the ad-hoc docker-compose environment, run  
> `DEV=true pytest`  
> while all the services are up and running: this will pollute you development database a bit with some test data, but it is much faster

## Architectural considerations
#### Authentication
Authentication is performed via JWT access tokens + JWT refresh tokens (which are rotated at every refresh and stored in the database in order to allow session banning): with appropriate secret-sharing mechanisms, this configuration prevents the need for backend services to call a stateful user session holder (e.g. Redis) on every API call.  
Access tokens are saved in localStorage whilst refresh token are stored inside secure, HTTP only cookies.  
Saving access tokens in localStorage is not ideal since it exposes them to XSS attacks, but this choice comes from early stages of development where I wanted to use the same access token to authenticate both API calls and websocket connections and I was leveraging a websocket library that wasn't able to read Cookies inside "on connect" event handler; now, since Socket.IO can access them, a nice and easy fix would be to store access tokens in secure Cookies as well.

#### Caching
There are 2 Redis instances - one for chat/notifications and one for caching - in order not to have a single point of failure: a crash of cache backend shouldn't affect messaging! This is also the reason why backend code ignores failed cache calls (it just logs them) and goes on querying PostgreSQL/Neo4j to preserve Bunnybook functionality.  
Most of caching follows Cache-Aside strategy. To store paginated results, only basic Redis data structures have been used, although I've also made some tests  with sorted sets (ranked by post/comment/message/... creation date) and more complex logic in order to handle frequently changing data collections.

#### Chat
Chat-related database tables have been designed to support group chats in the future, although currently only private chats (1-to-1) are implemented.  
To implement friends online/offline status, every websocket periodically sends a "I'm online!" message that sets a key on Redis ("websockets:{profile_id}") with short expiration time; a job is in charge of updating connected users friends' statuses, performing an MGET on Redis, using the recipient's friends' ids as keys, which are conveniently stored in Socket.IO session.  
The simpler approach of setting "online" status of a profile when its websocket completes authentication successfully and setting it as "offline" when it disconnects is not viable because 1) if the backend instance - to which the websocket is connected - crashes, the Redis key doesn't get cleared and the friend appears as "online" forever 2) it doesn't support multiple logins from different devices/browsers, because disconnecting from a single device would incorrectly show the user as "offline".

#### Databases
Neo4j have been introduced alongside PostgreSQL to handle profiles relationships in a convenient way, allowing fast queries like "bunnies you may know" or "mutual friends" that would have been complex and/or slow with a traditional RDBMS.  
Neo4j Bolt driver doesn't natively expose an async interface, so all calls are executed in separate threads (taken from a thread pool) not to block the main event loop. HTTP APIs + httpx could have been used to avoid the need for run_in_executor calls, at the cost of less convenient responses parsing and slightly worse performance (tested: still a valid solution in my opinion).  
<br/>
For PostgreSQL access, SQLAlchemy have been used asynchronously in "Core" mode; async "ORM" mode is quite new and - to use it correctly - some precautions must be taken to prevent implicit IO. Generally speaking, for CRUD-like apps (like Bunnybook) that don't involve a lot of business logic and complex objects interactions, I prefer to avoid ORMs and stick with query-builder libraries to have more control over the generated queries.  
PostgreSQL connection pooling via pgbouncer is currently not used since encode/databases under the hood creates an asyncpg-managed connection pool; in order to increase scalability, a NullPool-like pool object should be used, overriding current encode/databases PostgreSQL backend adapter implementation.  
In addition, PostgreSQL "pg_trgm" module as well as "gin" indexes have been added to speed up text search queries.

#### Dependency Injection
I made large use of dependency injection techniques both in frontend (microsoft/tsyringe) and backend (injector), where I extended standard FastAPI DI framework to make it compatible with "injector" package using a small utility function. Although some people might consider the extensive use of DI in Python an overkill since you have module imports, I still prefer to use it to have better control over instances initialization, easier testing and clearer dependency graph.

#### Frontend
RxJs stores have been chosen to manage state on the frontend. Coming from an Angular 2+ background, I have experience with Reactive Programming and I love working with RxJs since I think it is a really great tool to solve frontend state management issues, so I came up with a custom implementation of Angular services layer, leveraging RxJs stores + microsoft/tsyringe Dependency Injection framework. I had a great experience with this combo and I think I will reuse it for future projects. I like (and worked with) Redux / ReduxToolkit as well, but for small-to-medium sized projects I prefer the RxJs solution a little bit more since it feels more lightweight to me, also because including RxJs in the project allows me to use all its features for other tasks (not only state management).

#### Model
Backend model layer is made of pydantic classes, following the Anemic Domain Model pattern. Pydantic is a great way to represent domain model, ensuring continuous data validation and enforcing type hints at runtime. Regarding Anemic Domain Model, some people consider it an "anti-pattern": I respectfully disagree. Both Rich Domain Model and Anemic Domain Model have their reason to exist, what really matters is knowing why you are choosing one over the other and being aware of the pros/cons of each conceptual model.

## Development ideas and open issues
- implement "Likes" feature
- cache notifications and chat messages
- reimplement chat database schema to use a more "modern" approach, in order to leverage PostgreSQL 9.6+ recursive queries
- rate limit Socket.IO events
- store JWT access tokens the same way as JWT refresh tokens (secure + HTTP only + same site Cookies)
- take countermeasures against cache stampede (e.g. through locking)
- improve "RESTfulness" of profiles API
- better frontend error handling
- cleanup frontend "chat" code, which is a little bit messy and overcomplicated
- increase test coverage, adding more integration tests, as well as unit and functional tests
