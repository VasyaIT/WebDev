# WebDev

### First you need to log in to Stripe

>**Install stripe-cli https://stripe.com/docs/stripe-cli**

>**Up the webhook**: `stripe listen --forward-to localhost/payments/webhook/`

### Next, create the .env and .env_db files and make your settings there

+ **Also enter the stripe keys**

## Up the project
```commandline
docker compose up --build
```
### Create migrations and execute them
```commandline
docker compose exec web python webdev/manage.py makemigrations
```
```commandline
docker compose exec web python webdev/manage.py migrate
```
### Create a superuser
```commandline
docker compose exec web python webdev/manage.py createsuperuser
```