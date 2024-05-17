# Flask API Documentation

## Overview

This is a simple Flask API for managing stores and transactions. The API provides endpoints for adding, retrieving, updating, and deleting items in the `store` and `transaction` tables.

## Endpoints

### /api/store

#### POST /api/store

Add a new item to the store.

- **URL:** `/api/store`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "user_id": <integer>,
    "harga": <integer>,
    "nama": <string>,
    "deskripsi": <string>,
    "kategori": <string>
  }
Response:
json
Salin kode
{
  "message": "Store added successfully"
}
GET /api/store
Retrieve all items from the store.

URL: /api/store
Method: GET
Response:
json
Salin kode
[
  {
    "id": <integer>,
    "user_id": <integer>,
    "harga": <integer>,
    "nama": <string>,
    "deskripsi": <string>,
    "kategori": <string>
  },
  ...
]
GET /api/store/int:item_id
Retrieve a store item by its ID.

URL: /api/store/<int:item_id>
Method: GET
Response:
json
Salin kode
{
  "id": <integer>,
  "user_id": <integer>,
  "harga": <integer>,
  "nama": <string>,
  "deskripsi": <string>,
  "kategori": <string>
}
PUT /api/store/int:item_id
Update a store item by its ID.

URL: /api/store/<int:item_id>
Method: PUT
Request Body:
json
Salin kode
{
  "user_id": <integer>,
  "harga": <integer>,
  "nama": <string>,
  "deskripsi": <string>,
  "kategori": <string>
}
Response:
json
Salin kode
{
  "message": "Store updated successfully"
}
DELETE /api/store/int:item_id
Delete a store item by its ID.

URL: /api/store/<int:item_id>
Method: DELETE
Response:
json
Salin kode
{
  "message": "Store deleted successfully"
}
/api/transaction
POST /api/transaction
Add a new transaction to the transaction table.

URL: /api/transaction
Method: POST
Request Body:
json
Salin kode
{
  "store_id": <integer>,
  "user_id": <integer>,
  "status": <string>
}
Response:
json
Salin kode
{
  "message": "Transaction added successfully"
}
GET /api/transaction
Retrieve all transactions from the transaction table.

URL: /api/transaction
Method: GET
Response:
json
Salin kode
[
  {
    "id": <integer>,
    "store_id": <integer>,
    "user_id": <integer>,
    "status": <string>
  },
  ...
]
GET /api/transaction/int:trans_id
Retrieve a transaction by its ID.

URL: /api/transaction/<int:trans_id>
Method: GET
Response:
json
Salin kode
{
  "id": <integer>,
  "store_id": <integer>,
  "user_id": <integer>,
  "status": <string>
}
PUT /api/transaction/int:trans_id
Update a transaction by its ID.

URL: /api/transaction/<int:trans_id>
Method: PUT
Request Body:
json
Salin kode
{
  "store_id": <integer>,
  "user_id": <integer>,
  "status": <string>
}
Response:
json
Salin kode
{
  "message": "Transaction updated successfully"
}
DELETE /api/transaction/int:trans_id
Delete a transaction by its ID.

URL: /api/transaction/<int:trans_id>
Method: DELETE
Response:
json
Salin kode
{
  "message": "Transaction deleted successfully"
}
Error Handling
All endpoints will return an error message in JSON format if the request is invalid or if there is an issue processing the request. For example:

json
Salin kode
{
  "error": "Invalid request format"
}
Running the Application
To run the Flask application, use the following command:

sh
Salin kode
python app.py
Make sure you have all the dependencies installed:

sh
Salin kode
pip install -r requirements.txt
Database Initialization
Before running the application for the first time, initialize the database:

sh
Salin kode
python
>>> from app import db
>>> db.create_all()
>>> exit()
This will create the necessary tables in the SQLite database.

Contact
For any questions or issues, please contact [Your Contact Information].

css
Salin kode

Pastikan untuk mengganti `[Your Contact Information]` dengan informasi kontak Anda. README ini memberikan pandua