# Server escape

## TODO
 - Hire a new intern
 - Ask him to write the README (because that's all you left him !)

## How to build

The following should do the trick

 ```
 	docker-compose up
 ```

After starting the database for the first time, user's credentials need to be created:
 - Access the running container : `docker exec -it mongo bash`
 - Run mongo client : `mongo -u admin -p` and enter the admin password
 (admin credentials are set in the docker-compose.yml file, default are admin:password)
 - Create a new user (for the Python server):
 `db.createUser({user: 'apiuser', pwd: 'apipassword', roles: [{role: 'readWrite', db: 'nodes'}]}) `
 - Ask your boss to reward you for this hard work.
 - Go have a beer with the interns. <3
 - When ?

To rebuild containers (when editing the server for instance):

 ```
 	docker-compose up --build
 	# OR 
 	docker-compose build --no-cache
 	docker-compose up
 ```

Each module can be run separatly without docker compose:
 ```
 	docker-compose up --build
 ```

 ### Frontend

