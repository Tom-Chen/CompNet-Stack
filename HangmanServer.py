import morsockets as CN_Sockets, sys
from Libraries import utilities

class HangmanServer(object):
   
    def __init__(self):
        self.server_addr = ('192.168.66.65',99)
        self.client_addr = ('192.168.66.65',98)
        self.sock = CN_Sockets.socket(2,2)
        self.sock.settimeout(2.0)
        self.sock.bind(self.server_addr)
        self.original_word = input("Enter a word to use: ").upper()
        if not(self.original_word.isalpha()):
            print("Letters only, please.")
            self.sock.close()
            sys.exit()
        self.word = self.original_word
        self.guessed = []
        self.lives = 5
        
        def print_and_reply(reply):
            print(reply)
            self.sock.sendto(reply.encode("UTF-8"),self.client_addr)
        
        while True:
            try:
                bytearray_msg, source_address = self.sock.recvfrom(8192)
                source_IP, source_port = source_address
                message = utilities.forcedecode(bytearray_msg)
                print(message)
                
                if len(message) == 1:
                    letter = message.upper()
                    if letter.isalpha():
                        print("Guess: " + letter)
                        
                        if letter in self.guessed:
                            already_guessed_reply = "Letter has already been guessed"
                            print_and_reply(already_guessed_reply)
                            
                        elif letter in self.word:
                            self.guessed.append(letter)
                            self.word = self.word.replace(letter,"_")
                            
                            complete = True
                            for char in self.word:
                                if char != "_":
                                    complete = False
                            if complete == True:
                                victory_reply = "Congratulations The word was " + self.original_word
                                print_and_reply(victory_reply)
                                self.sock.close()
                                sys.exit()
                            else:
                                word_length = len(self.original_word)
                                display_word = "7" * word_length
                                for i in range(word_length):
                                    if self.word[i] == "_":
                                        display_word = display_word[:i] + self.original_word[i] + display_word[i+1:]
                                
                                valid_reply = "Word so far " + display_word
                                self.sock.sendto(valid_reply.encode("UTF-8"),self.client_addr)
                                print("Remaining Letters " + self.word)
                                
                        else:
                            self.guessed.append(letter)
                            self.lives -= 1
                            
                            if self.lives <= 0:
                                game_over_reply = "Game over The word was " + self.original_word
                                print_and_reply(game_over_reply)
                                self.sock.close()
                                sys.exit()
                                
                            else:
                                incorrect_reply = "Sorry that guess was incorrect You have " + str(self.lives) + " chances remaining"
                                print_and_reply(incorrect_reply)
                            
                    else:
                        invalid_reply = "Invalid input packet received"
                        print_and_reply(invalid_reply)
                        
                else:
                    invalid_reply = "Invalid input packet received"
                    print_and_reply(invalid_reply)
                        
            except CN_Sockets.TimeoutException:
                sys.stdout.write(".")
                sys.stdout.flush()
                continue
            
            


if __name__ == "__main__":
    HangmanServer()
