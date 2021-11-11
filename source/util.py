from os import path, mkdir
import sympy

class CustomException(BaseException):
    def __init__(self, message):
        super().__init__(message)

class RSA:
    def __init__(self):
        pass

    def set_keys(self, e, d, N):
        self.enc_pair = (e, N)
        self.dec_pair = (d, N)

    def generate_keys(self):
        x = sympy.randprime(1000, 2**15)
        y = sympy.randprime(1000, 2**15)
        N = x * y
        T = (x-1) * (y-1)
        e = sympy.randprime(2, T >> 1)
        d = sympy.mod_inverse(e, T)
        self.enc_pair = (e, N)
        self.dec_pair = (d, N)

    def encrypt(self, m):
        e, N = self.enc_pair
        return pow(ord(m),e,N)

    def decrypt(self, c):
        try:
            d, N = self.dec_pair
            return chr(pow(c, d, N))  
        except ValueError:
            return '?'
        

#Vault that exposes interface for interaction with main window
class Vault(RSA):
    def __init__(self):
        super().__init__()
        if (not path.isdir('./vault')):
            mkdir('./vault')
    
    #Parses key string
    def parse_key(self, key):
        try:
            key = key.replace(' ', '')
            key = key.split('-')
            e, d, N = int(key[0]), int(key[1]), int(key[2])
            return (e, d, N)

        except BaseException:
            raise CustomException("Failed to parse the key...")
    
    #Key required before using any of below methods
    def read(self, path):
        try:
            with open(path, 'br') as vault:
                string = ''
                while (True):
                    c = int.from_bytes(vault.read(4), 'little', signed=True)
                    if (not c):
                        break
                    p = self.decrypt(c)
                    string += p
                return string
        except BaseException:
            raise CustomException(f"Failed to decrypt {path} ...")

    #Overwrites existing or creates new vault
    def overwrite(self, data, file_path):
        if (not path.isdir('./vault')):
                mkdir('./vault')
        try:
            with open(file_path, 'wb+') as vault:
                for p in data:
                    c = self.encrypt(p)
                    vault.write(c.to_bytes(4, 'little'))
                newline = self.encrypt('\n')
                vault.write(newline.to_bytes(4, 'little'))
        except BaseException:
            raise CustomException(f"Failed to overwrite {path} ...")

    #Encrypts existing file and creates new vault
    def create_from_file(self, file_path):
        try:
            #If folder 'vault' was accidentally deleted during program run then saving any new vaults 
            #will crash the program. To avoid that, folder needs to be created again.
            if (not path.isdir('./vault')):
                mkdir('./vault')
            
            save_path = f'./vault/{path.splitext(path.basename(file_path))[0]}.vault'
            
            with open(file_path, 'r') as infile:
                data = infile.read()
                self.overwrite(data, save_path)

            self.vault = save_path   
        except BaseException:
            raise CustomException(f"Failed to create file {file_path} ...")


