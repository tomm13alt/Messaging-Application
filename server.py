# 25/1/2023
# V13.3

from math import sqrt, gcd
from socket import socket, gethostname, gethostbyname
import time
from random import randint
from threading import Thread


class Security:
    # Generates key and port, as well as encrypting and decrypting messages/ keys
    def __init__(self):
        self.d = None
        self.e = None
        self.N = None
        self.cipherKey = None
        self.encryptedCipherKey = None

    def getKeys(self):
        # Uses algorithms in modular exponentiation to generate the RSA private, public
        # And cipher key
        e = 0
        d = 0
        N = 0
        P = 0
        Q = 0

        lower = 100
        upper = 9999

        primes = []
        coprimes = []

        for prime in range(lower, upper):
            isPrime = True

            for factor in range(2, int(sqrt(prime) + 1)):
                if prime % factor == 0:
                    isPrime = False
                    break

            if isPrime is True:
                primes.append(prime)

        while True:
            # Generate 2 primes P and Q where the product N is 6 digits
            P = primes[randint(0, len(primes) - 1)]
            Q = primes[randint(0, len(primes) - 1)]

            # N is the 7-12th digits of either the public or private key
            self.N = P * Q

            phiN = (P - 1) * (Q - 1)

            if len(str(self.N)) == 6:
                break

        # Generate e such that e < phiN, 6 digits long, as well as coprime with phiN
        for coprime in range(100000, phiN):
            if gcd(coprime, phiN) == 1:
                coprimes.append(coprime)

        self.e = coprimes[randint(0, len(coprimes))]

        for k in range(1, upper ** 2):
            # Generate d such that d = e^-1 mod phiN and is 6 digits long
            if (k * phiN + 1) % self.e == 0:
                if (k * phiN + 1) // self.e != self.e and len(str((k * phiN + 1) // self.e)) == 6:
                    self.d = (k * phiN + 1) // self.e
                    break

        self.cipherKey = randint(1, 26)
        self.encryptedCipherKey = self.rsaEncrypt(self.cipherKey, self.e, self.N)

        print(f"[Server] Public key = {e}{N}")
        print(f"[Server] Private key = {d}{N}")
        print(f"[Server] Cipher key = {self.encryptedCipherKey}")

    @staticmethod
    def rsaEncrypt(key, e, N):
        rsaKey = pow(key, e, N)

        return rsaKey

    @staticmethod
    def rsaDecrypt(key, d, N):
        newKey = pow(key, d, N)

        return newKey

    @staticmethod
    def caesarEncrypt(message, cipherKey):
        newMessage = ""
        for letter in message:

            if letter.isalpha() is True:

                if letter.islower() is True:
                    step = 97

                elif letter.isupper() is True:
                    step = 65

                else:
                    raise ValueError("Invalid character")

                index = (ord(letter) + cipherKey - step) % 26

                newMessage += chr(index + step)

            else:
                newMessage += letter

        return newMessage

    @staticmethod
    def caesarDecrypt(message, cipherKey):
        newMessage = ""
        for letter in message:

            if letter.isalpha() is True:

                if letter.islower() is True:
                    step = 97

                elif letter.isupper() is True:
                    step = 65

                else:
                    raise ValueError("Invalid character")

                index = (ord(letter) - cipherKey - step) % 26

                newMessage += chr(index + step)

            else:
                newMessage += letter

        return newMessage


class Send:
    @staticmethod
    def broadcast(message):
        # Send a public message to every client
        print(f"[Public] {message}")

        for client in connectionInstance.clients:
            client.send(securityInstance.caesarEncrypt(message, securityInstance.cipherKey).encode())

    @staticmethod
    def broadcastDisplay(message):
        # Sends a public animated banner with {message} parameter
        print(f"[PublicDisplay] {message}")

        for client in connectionInstance.clients:
            client.send(securityInstance.caesarEncrypt(f"/display {message}", securityInstance.cipherKey).encode())

    @staticmethod
    def privateBroadcast(message, clientSocket):
        # Send a private message to 1 specific client
        if clientSocket in connectionInstance.clients:
            print(f"[Private] {message}")

            clientSocket.send(securityInstance.caesarEncrypt(message, securityInstance.cipherKey).encode())

    @staticmethod
    def privateBroadcastDisplay(message, clientSocket):
        # Sends a private animted banner with {message} parameter
        if clientSocket in connectionInstance.clients:
            print(f"[PrivateDisplay] {message}")

            clientSocket.send(securityInstance.caesarEncrypt(f"/display {message}", securityInstance.cipherKey).
                              encode())

    @staticmethod
    def command(message, username, clientSocket):
        # Use list to prevent doubled code
        if message == "/leave":
            connectionInstance.removeUser(username, clientSocket)
        elif message[0:6] == "/color" or message[0:7] == "/border" or message[0:9] == "/savechat":
            sendInstance.privateBroadcast(message, clientSocket)
        elif message in ["/theme", "/ldm", "/previous", "/next"]:
            sendInstance.privateBroadcast(message, clientSocket)
        else:
            sendInstance.privateBroadcastDisplay("Your command is unknown", clientSocket)


class Connection:
    def __init__(self):
        self.socket = socket()
        self.host = gethostbyname(gethostname())
        self.port = randint(49125, 65535)
        self.userOnline = 0
        self.users = []
        self.clients = []

    def bindToSocket(self):
        # Binds to an open port within the range 49125-65536
        while True:
            try:
                if self.host == '127.0.0.1' and __name__ == '__main__':
                    self.host = input("[Server] Failed to bind - Enter an IP to host the server on\n")

                self.socket.bind((self.host, self.port))

            except ConnectionError:
                self.port = randint(49125, 65536)

            except OSError:
                self.host = input("[Server] Failed to bind - Enter an IP to host the server on\n")

            else:
                print(f"[Server] Server hosted on {str(self.host)} on port {str(self.port)}")
                break

    def connect(self):
        # After binding, receive incoming requests
        self.bindToSocket()
        self.socket.listen()

        securityInstance.getKeys()

        while True:
            # The main thread listens for incoming connections and accepts it
            # This also broadcasts to other online users that a new user has connected.

            clientSocket, Address = self.socket.accept()

            self.clients.append(clientSocket)

            username = securityInstance.caesarDecrypt(clientSocket.recv(1024).decode(), securityInstance.cipherKey)

            # Criteria for a valid username: doesn't already exist, has no spaces, and is under 11 characters
            if self.validateUsername(username) is True:
                # Allows the user to join the chatroom, send and receive messages
                self.addUser(username)

                # Initialise an update thread given the username is valid
                Thread(target=self.listen, args=[username, clientSocket, True]).start()
                print(f"[Thread] Started {username}'s update thread. Username is valid")

            else:
                sendInstance.privateBroadcast("/reject", clientSocket)

                # Initialise an update thread given the username is invalid
                Thread(target=self.listen, args=[username, clientSocket, False]).start()
                print(f"[Thread] Started {username}'s update thread. Username is invalid")

    def listen(self, username, clientSocket, hasValidUsername):
        # A listening thread linked to every unique client, and detects input from them
        if hasValidUsername is False:
            while hasValidUsername is False and clientSocket in self.clients:
                try:
                    signal = securityInstance.caesarDecrypt(clientSocket.recv(1024).decode(),
                                                            securityInstance.cipherKey)

                    if signal:
                        if signal == "/leave":
                            # If the user quits after failing to input a valid username, remove them
                            self.removeUser(None, clientSocket)

                        if self.validateUsername(signal) is True:
                            # Allow the client to receive and accept messages
                            self.addUser(signal)

                            username = signal
                            hasValidUsername = True

                        else:
                            sendInstance.privateBroadcast("/reject", clientSocket)

                except (ConnectionResetError, OSError) as e:
                    print(f"[Thread] An error occured in {username}'s update thread before validtion completed. {e}")
                    self.removeUser(None, clientSocket)

        messagesSentRecently = 0
        lastMessageSentTime = 0
        warnUser = False
        detectSpam = True

        while hasValidUsername is True and clientSocket in self.clients:
            try:
                signal = securityInstance.caesarDecrypt(clientSocket.recv(1024).decode(), securityInstance.cipherKey)
                unifiedmessage = f"{username}: {signal}"

                if signal:
                    if signal[0] == "/":
                        sendInstance.command(signal, username, clientSocket)

                    else:
                        if detectSpam is True:
                            if messagesSentRecently >= 3:
                                if warnUser is False:
                                    sendInstance.privateBroadcast("/timeout You are sending messages too quickly",
                                                                  clientSocket)
                                    warnUser = True

                                if time.time() > lastMessageSentTime + 5:
                                    messagesSentRecently = 0
                                    warnUser = False

                            else:
                                if self.validateMessageLength(unifiedmessage) is False:
                                    sendInstance.privateBroadcast("/timeout Your message is too long", clientSocket)

                                else:
                                    sendInstance.broadcast(unifiedmessage)

                                if lastMessageSentTime + 1 > time.time():
                                    messagesSentRecently += 1

                                elif messagesSentRecently > 0:
                                    messagesSentRecently -= 1

                                lastMessageSentTime = time.time()

                        else:
                            if self.validateMessageLength(unifiedmessage) is False:
                                sendInstance.privateBroadcast("/timeout Your meessage is too long", clientSocket)

                            else:
                                sendInstance.broadcast(unifiedmessage)

            except (ConnectionResetError, OSError) as e:
                print(f"[Thread] An error occured in {username}'s update thread after validation completed. {e}")
                self.removeUser(username, clientSocket)

        print(f"[Thread] Closed {username}'s update thread")

    def addUser(self, username):
        # Adds user to the list of users and updates everyone's user lists
        self.users.append(username)
        self.userOnline += 1

        message = "/accept "

        for user in self.users:
            message += f"{user} "

        sendInstance.broadcast(message)

    def removeUser(self, username, clientSocket):
        # Called when a user has a duplicate username or leaves
        clientSocket.close()

        if clientSocket in self.clients:
            self.clients.remove(clientSocket)

        if username in self.users:
            self.users.remove(username)
            self.userOnline -= 1

        sendInstance.broadcast(f"/remove {username}")

    def validateUsername(self, username):
        # Criteria for a valid username: doesn't already exist, has no spaces, and is under 11 characters
        if username in self.users or " " in username or len(username) > 7 or len(username) < 1 or username == "None":
            return False

        else:
            return True

    @staticmethod
    def validateMessageLength(message):
        if len(message) > 50:
            return False

        else:
            return True


connectionInstance = Connection()
securityInstance = Security()
sendInstance = Send()

if __name__ == '__main__':
    connectionInstance.connect()
