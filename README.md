# uw-restclients-spotseeker

A REST client for the Scout clients to securely communicate with the Spotseeker Server application

## Running uw-restclients-spotseeker

To run the test application, you'll need a running spotseeker_server instance, then `cd` into the `uw_spotseeker` directory and run `docker-compose up`.

## Running Tests

### Unit Tests

To run the tests, you'll need to `cd` into the `uw_spotseeker` directory and run `docker exec -ti (spotseeker_app_name) bin/python manage.py test`.

### Blackbox Tests

There's a test app named test-app in the `docker/` directory in this repo. You will need to use this app to test the spotseeker server to restclient communication. To do this, you'll need to run the `uw-restclients-spotseeker` application as stated above, but set a desired `PORT` for the test-app in the `.env` file. Then, start up `spotseeker-server` in live mode.

#### Authentication

`spotseeker-server` uses OAuth2 client credentials to register and validate applications attempting to communicate with it. To register the test-app, you'll need to run the following command:

`docker exec -ti spotseeker-server bin/python manage.py register_application [--show-credential/-s]`

When prompted, enter the name of the testing app, `test-app` and the command will proceed to print out the credential for the application. You'll need to copy this credential and paste it into the `.env` file for `CREDENTIAL`.

#### Using the Test App

Once both applications are running and authenticated, you can run the blackbox tests by opening a browser to `http://localhost:PORT/` and try using all the functions in the spot interface. All pages will show the set scope and access token being used to communicate with the spotseeker server. You can filter the spots by app type, and you can click on each spot to "GET" that specific spot. From here you can also edit and delete the spot or delete and post images, which should only work with a write scope. For certain tech spots, you can also interact with the items that are in the spot view.
##### Caching

The REST client has an option for caching the access token it receives from the server. This is done by setting the `DEBUG_CACHING` variable in the `.env` file to `True`. This will cache the access token in local memory and the token expires every hour, where it will be automatically refreshed. If you don't want caching to confirm that different access tokens are received every time, set the environment variable to `False`.
