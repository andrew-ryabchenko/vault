
# Vault

Encrypted offline storage that allows anyone to keep their sensitive data locally and secure.


## Documentation
The current version is built for Windows only.

To run Vault execute `vault.exe`. 

#### Important concepts
- `.vault` files contain encrypted data. By default they are created in `vault` folder.
- Multiple `.vault` files can be created and managed.
- With every new `.vault` file program generates unique random passcode that is used to access and modify `.vault`
- Program does not store passcode and displays it only once. 
- `File` -> `New` option allows to create new vault from existing textual file. Alowed extensions are .txt, .csv, .tsv. 


## Authors

- [@andrew-ryabchenko](https://www.github.com/andrew-ryabchenko)

## This is an open-source application

Source code is located in `source` folder.