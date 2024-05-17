# Flask API Documentation

## Endpoints

### /api/store

- **POST /api/store**: Add a new item to the store.
- **GET /api/store**: Retrieve all items from the store.
- **GET /api/store/int:item_id**: Retrieve a store item by its ID.
- **PUT /api/store/int:item_id**: Update a store item by its ID.
- **DELETE /api/store/int:item_id**: Delete a store item by its ID.

### /api/transaction

- **POST /api/transaction**: Add a new transaction to the transaction table.
- **GET /api/transaction**: Retrieve all transactions from the transaction table.
- **GET /api/transaction/int:trans_id**: Retrieve a transaction by its ID.
- **PUT /api/transaction/int:trans_id**: Update a transaction by its ID.
- **DELETE /api/transaction/int:trans_id**: Delete a transaction by its ID.
