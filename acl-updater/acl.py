from __future__ import print_function
from jsonrpclib import Server
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

class ACL():

    def __init__(self, ip, username, password):
        switchURL = "https://{}:{}@{}/command-api".format(username, password, ip)
        self.switch = Server(switchURL)

        self.ip = ip

# Adds the rule to the ACL. Only supply the rule, no need to supply the sequence. 
# This will check after it adds the ACL that the ACL was added
# Returns bool
    def add_to_acl(self, rule, acl, seq_step):

        seq = self.__get_next_seq(acl,seq_step)
        if seq == -99:
            return False

        cmd = ["enable", "configure", "ip access-list " + acl, str(seq) + " " + rule]
        self.__runCMD(cmd)

        if self.__get_seq(seq, acl) == rule:
            return True

        return False

    def remove_host_from_acl(self, host, acl):
        cmd = ["enable", "show ip access-lists " + acl]
        response = self.__runCMD(cmd)

        sequence_numbers = []

        for sequence in response[1]['aclList'][0]['sequence']:
            for text in sequence['text'].split():
                if host == text:
                    sequence_numbers.append(sequence['sequenceNumber'])
                    break

        if not sequence_numbers:
            print("Host not in ACL")
            return False

        removed_sequence_results = []

        for sequence_number in sequence_numbers:
            removed_sequence_results.append(self.__delete_rule(sequence_number, acl))

        if False in removed_sequence_results:
            #print("Failed to remove all rules")
            return False
        else:
            #print("Removed all rules")
            return True

        return False


    def __delete_rule(self, seq, acl):
        cmd = ["enable", "configure", "ip access-list " + acl, "no " + str(seq)]
        self.__runCMD(cmd)
        
        if self.__get_seq(seq, acl) == -99:
            return True

        return False

    def __get_seq(self, seq, acl):
        cmd = ["enable", "show ip access-lists " + acl]
        response = self.__runCMD(cmd)

        for sequence in response[1]['aclList'][0]['sequence']:
            if str(sequence['sequenceNumber']) == str(seq):
                return sequence['text']

        return -99

    def __get_next_seq(self, acl, seq_step):
        cmd = ["enable", "show ip access-lists " + acl]
        response = self.__runCMD(cmd)

        action_count = 0

        for i, sequence in enumerate(response[1]['aclList'][0]['sequence'][::-1]):
            if 'action' in  sequence and i is not 0:
                action_count+1
                return int(sequence['sequenceNumber'])+seq_step


        if len(response[1]['aclList'][0]['sequence']) == 0 or len(response[1]['aclList'][0]['sequence']) == 1 or action_count == 0:
            #print("Seems like there are no rules, we will begin with 10")
            return 10
        
        return -99

    def __runCMD(self, cmd):
        try:
            response = self.switch.runCmds( 1, cmd )
            return response
        except:
            print("Error with connecting to " + self.ip + " Please try again.")
            quit()


