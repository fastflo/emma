# Emma database providers technical description
Emma Database provider is a set of classes which handle all work between Emma UI and database itself.

## Host class
Host class provides a main connection to DB and should support following methods:



### Connection methods:

#### connect(self)
Opens connection

#### close(self)
Closes connection

#### get\_connection\_string(self)
To be used in saving config

### Escaping values:

#### escape(self, value)
Escape field value

#### escape_field(self, field_name)
Escape field name

#### escape_table(self, table_name)
Escape table name

#### escape_db(self, db_name)
Escape Database name

### Common functions:

#### ping
Pings server connection

#### query
Runs a query

#### refresh
Refreshes databases

#### *select_database*
Selects specific database to work with

#### *insert_id(self)*
Get last insert id after INSERT command executed

#### *use_db*
#### *is_at_least_version*
#### *set_update_ui*
#### *refresh_processlist*
