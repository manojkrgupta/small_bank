### Plan
* The plan is to relinquish authentication from code and give it to standard IAM tools like keycloak.
* User account management, Profile management, Roles, Group, Permissions etc all are moved to keycloak.
* The plan is also to demonstrate Python3 FastAPI integration with keycloak and MongoDB. 

### Story
* In this example, we are trying to show a Banking application.
* Allow Banks to create accounts (user accounts)
* Allow Users to add fund and withdraw (debit, credit)
* In this example, we have two types of Role:
  * Role = bank_teller:
    * for every bank there will be a user like (icici_teller) belonging to this role.
    * This role/user will be able to create account(users account) for new customer.
    * This role/user can see deposits in account.
    * But, will not be able to add or withdraw from account.
  * Role = account_owner:
      * This is a general bank account user role. Example bob and charlie
      * This role/user will be able to add and/or withdraw from his/her account.
      * This role/user will be able to see fund balance in his/her account.
* We also have two Groups:
  * Group = hdfc:
    * User list: charlie, hdfc_teller
  * Group = icici:
    * User list: bob, icici_teller

### Tabular Summary of URI, Method, Keycloak Role and Keycloak Users having permissions

| Present URL                | Method | Description                        | Allowed by Roles | Users having this permission |
|----------------------------|--------|------------------------------------|------------------|------------------------------|
| /bank_user/{bank}          | GET    | to see balance                     | account_owner    | bob, charlie                 |
| /bank_user/{bank}          | PUT    | to transact (credit or debit)      | account_owner    | bob, charlie                 |
| /bank_teller/{bank}/{user} | PUT    | to create account for user in bank | bank_teller      | icici_teller, hdfc_teller    |
| /bank_teller/{bank}/{user} | GET    | to get balance for every account   | bank_teller      | icici_teller, hdfc_teller    |

### Start environment
```
]$ cd docker/
]$ mkdir keycloak_data
]$ mkdir mongodb_data
]$ sudo docker login
]$ sudo docker compose -f docker_compose_keycloak_mongodb.yml --env-file docker_compose_env up
```

### URL
* MongoDB web  -- http://localhost:8084
* Keycloak     -- http://localhost:8085
* Application  -- http://localhost:8086

### Ensure mongodb is initialised (Below is a method from shell. You can also login to MongoDB web)
* You will see database named=small_banks is auto created
* You will see collection named=banks.hdfc and banks.icici is also auto created
```
]$ sudo docker exec -it mongodb bash
root@mongodb:/# mongosh -u admin -p 
Enter password: <get_password_from_file docker_compose_env>

test> show dbs
...
small_banks   24.00 KiB
test> 

test> use small_banks
switched to db small_banks

small_banks> show collections
banks.hdfc
banks.icici
small_banks>
small_banks> db.banks.hdfc.find({})
small_banks> db.banks.icici.find({})
small_banks>
```

### Initialise keycloak
* go to keycloak http://127.0.0.1:8085/
* login with admin (password in file=docker/docker_compose_env)
* Select Keycloak drop down from top left -> Create realm -> Browser -> Select file docker/small_bank_init_keycloak.json -> Create
* After this you will see, below objects are auto created
  * realm   = small_bank 
  * client  = sm:api
  * user    = bob           (role=account_owner, group=icici)   default password=password
  * user    = charlie       (role=account_owner, group=hdfc)    default password=password
  * user    = icici_teller  (role=bank_teller  , group=icici)   default password=password
  * user    = hdfc_teller   (role=bank_teller  , group=hdfc)    default password=password
  
### Start application
```
]$ cd bin
]$ uvicorn main:app --log-level debug --port 8086 --host 127.0.0.1 --reload
```

### First API call
* Before users can use their account, bank teller needs to create account for bob and charlie 
* Go to http://127.0.0.1:8086/docs
  * Authenticate as icici_teller
  * Extend PUT /bank_teller/{bank}/{user}
  * Try, giving bank=icici, user=bob
* Now logout, restart browser or clear session for icici_teller from keycloak admin page
  * And, Authenticate as hdfc_teller
  * Extend PUT /bank_teller/{bank}/{user}
  * Try, giving bank=hdfc, user=charlie

### Note (warning|caution): 
  * In keycloak, bob belongs to group=icici and charlie belongs to group=hdfc
  * hence, we choose icici_teller to create bobs account
  * and, hdfc_teller to create charlie account
  * incase, icici_teller also creates account for charlie -- then charlie will have two accounts in both the banks
    * But, to use icici account, charlie will need to be also added in keycloak group=icici

### Test 1 -- Authenticate as bob(or charlie) and check balance
* GET    /bank_user/{bank}     # for bob use bank=icici, for charlie use bank=hdfc

### Test 2 -- Authenticate as bob(or charlie) and perform credit/debit operation
* PUT    /bank_user/{bank}     # for bob use bank=icici, for charlie use bank=hdfc

### An example of curl
```
curl -X 'PUT' \
'http://127.0.0.1:8086/bank_teller/icici/bob' \
-H 'accept: application/json' \
-H 'Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJVNm0zNG1rNW1ZVFNpaUpWcE9QTFZERjZpdkhoU094TnAwQ096dXJhRGljIn0.eyJleHAiOjE3MjUwODU0OTksImlhdCI6MTcyNTA4NTE5OSwiYXV0aF90aW1lIjoxNzI1MDg1MTk5LCJqdGkiOiIzY2QxNjRjNy1kMWM4LTQ5ZGUtYTAzMi1hMjYzZWNlMzJlYWUiLCJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjgwODUvcmVhbG1zL3NtYWxsX2JhbmsiLCJhdWQiOlsic206YXBpIiwiYWNjb3VudCJdLCJzdWIiOiJhNmMyMzliMi1mOWI5LTQ3MzctOTc4NC1lYWNhOTRiYTRiYzYiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJzbTphcGkiLCJzaWQiOiI5NDI4NmZjNS1jOTQ2LTQwYjYtYTFlNC04YWUyYzBhZWY0YWIiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly8xMjcuMC4wLjE6ODA4NiJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsImRlZmF1bHQtcm9sZXMtc21hbGxfYmFuayJdfSwicmVzb3VyY2VfYWNjZXNzIjp7InNtOmFwaSI6eyJyb2xlcyI6WyJiYW5rX3RlbGxlciJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJlbWFpbCBwcm9maWxlIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoiSUNJQ0kgVGVsbGVyIiwiZ3JvdXBzIjpbIi9pY2ljaSJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJpY2ljaV90ZWxsZXIiLCJnaXZlbl9uYW1lIjoiSUNJQ0kiLCJmYW1pbHlfbmFtZSI6IlRlbGxlciIsImVtYWlsIjoidGVsbGVyQGljaWNpLmNvIn0.xi7elqZ2EyfZrqWjkYAJwpHiJJxdUp8hwwhkXdECclkwd7Ds5hjymw6GYS2cy-cNa7Jz9escPYVYV1MyCN5O673FmPiIsnL2CdW4Mqf4236_20Uam71GcZpzSjs4DiYAm8KtsI8ux13FoklF1ou8S9Lml0Xh_XIG2-wq4jNnxxUlrlQMxgRllgEPme7oxIE4oJJkiOmVW2WFQWYeANKa7vhJ7IOe_mmiqzTn39vdGEmijxzfkE5hInmJtzW0-w9D0dTp5ZObAitxbth5-qupCzvgXwRmV-LM1gGNpNbIp7uKr_QdXZqsthpyURBC_KixR9IxN4RGHVeFybDCKUDaYA'
```