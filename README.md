# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Azure Resource | Service Tier | Monthly Cost |
| ------------ | ------------ | ------------ |
| *Azure Database for PostgreSQL* |  Single Server Deployment, Basic Tier, 1 Gen 5 (1 vCore) x 730 Hours, 5 GiB Storage, 100 GiB Additional Backup storage - LRS redundancy | $63,067 |
| *Service Bus* | Basic tier: 0 million messaging operations | $0.00 |
| *App Service* | Free Tier; 1 F1 (0 Core(s), 1 GB RAM, 1 GB Storage) x 730 Hours; Linux OS | $0.00 |
| *Azure Functions* | Consumption tier, Pay as you go, 128 MB memory, 100 milliseconds execution time, 10,000 executions/mo | $0.00 |
| *Storage Accounts* | Consumption tier, Pay as you go, 128 MB memory, 100 milliseconds execution time, 10,000 executions/mo | $25,044 |
| *Azure Communication Services* | Phone numbers leasing: 0 local and 0 toll-free United States (+1) phone number(s); Phone number lookup: 0 line type queries; Voice and Video Calling - over IP: 1 reoccurring call(s) (30 minutes X 0 call(s) per month X 0 participants per call); Call Recording: 0 Mixed audio recorded minutes, 0 Mixed audio and video recorded minutes, 0 Unmixed audio minutes for 0 participants; SIP Direct Routing: 0 Inbound calling minutes, 0 Outbound calling minutes; 0 connections X 0 minutes per connection X 1 Mbps upload speed; Chat: 0 chat users x 0 message(s) sent per chat user; Email: 10000 Email sent per month, 0 MB per Email; Whatsapp messaging: 0 Inbound messages, 0 Outbound messages; Job Router: 0 Jobs Routed per month | $2,50 |

Reference: <a href="https://github.com/ThachHQ/nd081-c3-Migrating-Non-Native-Cloud-Applications-project-starter/blob/master/screenshots/ExportedEstimate.xlsx">ExportedEstimate.xlsx</a>

## Architecture Explanation
- Azure Web App allows for the scalable hosting of the frontend, ensuring the application can handle increased traffic.

- Azure Functions handle backend, process user requests for data, handle background tasks, only pay for the compute resources used.

- Using both, it allows for easy deployment, cost optimization, and future expansion, while mitigating potential risks.
