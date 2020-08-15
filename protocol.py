from abc import abstractmethod, ABC
from shared import H, jacobi_symbol, powmod, evaluate_poly, _divmod

class IProtocolStrategy(ABC):    
    @abstractmethod
    def get_hashed_message(self): raise NotImplementedError
    @abstractmethod
    def calculate_share(self, x, si): raise NotImplementedError
    @abstractmethod
    def calculate_e_prime(self): raise NotImplementedError
    @abstractmethod
    def calculate_x_tilde(self, x): raise NotImplementedError
    @abstractmethod
    def calculate_secret_key_shares(self, coefficients, l): raise NotImplementedError
    @abstractmethod
    def calculate_y(self, wa, xb): raise NotImplementedError

class Protocol1(IProtocolStrategy):
    def __init__(self, message, n, delta, m):
        self.message = message
        self.n = n
        self.delta = delta
        self.m = m

    def get_hashed_message(self):
        return H(self.message, self.n)
    
    def calculate_share(self, x, si):
        return powmod(x, 2 * self.delta * si, self.n)
    
    def calculate_e_prime(self):
        return 4 * pow(self.delta, 2)

    def calculate_x_tilde(self, x):
        return powmod(x, 4 * self.delta, self.n)
        
    def calculate_secret_key_shares(self, coefficients, l):
        return [evaluate_poly(coefficients, i) % self.m for i in range(1, l + 1)]
    
    def calculate_y(self, wa, xb):
        return (wa * xb) % self.n

class Protocol2(IProtocolStrategy):    
    def __init__(self, message, n, delta, m, u, e):
        self.message = message
        self.n = n
        self.delta = delta
        self.m = m
        self.u = u
        self.e = e

    def get_hashed_message(self):
        x_hat = H(self.message, self.n)
        x = x_hat
        if jacobi_symbol(x_hat, self.n) == -1:
            x = (x_hat * pow(self.u, self.e, self.n)) % self.n
        assert jacobi_symbol(x, self.n) == 1
        return x
    
    def calculate_share(self, x, si):
        return powmod(x, 2 * si, self.n)
    
    def calculate_e_prime(self):
        return 4 
    
    def calculate_x_tilde(self, x):
        return powmod(x, 4, self.n)
    
    def calculate_secret_key_shares(self, coefficients, l):
        temp = pow(self.delta, -1, self.m)
        return [evaluate_poly(coefficients, i) * temp % self.m for i in range(1, l + 1)]
    
    def calculate_y(self, wa, xb):
        y = (wa * xb) % self.n
        if jacobi_symbol(H(self.message, self.n), self.n) == -1:
            y = _divmod(y, self.u, self.n)
        return y