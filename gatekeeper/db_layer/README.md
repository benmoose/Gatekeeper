# DB Layer

The purpose of this package is to define the DB schema and expose methods for accessing data in a controlled way.

`db_layer` is organised into a set of packages, each of which contain related models and interfaces.

#### Special packages
- `helpers` utility methods
- `migrations` Django's migration files

#### A note on permissions
Whilst there is a case for enforcing permissions at the DB layer (and in some cases this is appropriate) in general
interfaces should avoid implementing complex logic and stay small and focused.
Interface methods should rely on the caller to implement permission checking logic and and remain simple and focused.
This approach will help to keep the API surface small and access to the database generic.

Interfaces should, however, take care to implement integrity logic (such as start < end)
and raise errors upon receiving nonsensical input.
