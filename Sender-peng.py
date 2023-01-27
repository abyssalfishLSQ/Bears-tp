import sys
import getopt
import os
import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
# sys.argv =[sys.argv[0],'-fREADME','-p33122','-a127.0.0.1']
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        if filename == None:
            self.infile = sys.stdin
        else:
            self.infile = open(filename, "rb")

    # Main sending loop.
    def handle_response(self,response_packet):
        msg_type, seqno, data, checksum = self.split_packet(response_packet)
        if Checksum.validate_checksum(response_packet):

            # print "recv: %s" % response_packet
            return eval(seqno), True
        else:
            # print "recv: %s <--- CHECKSUM FAILED" % response_packet
            return eval(seqno), False

    def start(self):
        # raise NotImplementedError
        to = 0.5
        msg_size = 4000
        wnd = 5
        size = 0
        msg = []
        base = 0
        seqno = 0
        print os.path.getsize(filename)
        next_msg = self.infile.read(msg_size)
        while not next_msg == "":
            msg.append(next_msg)
            size += 1
            next_msg = self.infile.read(msg_size)
        msg.append(next_msg)
        size+=1
        msg_type = None

        # print size
        # msg = self.infile.read(500)

        while not msg_type == 'end':
            # next_msg = self.infile.read(500)
            # print seqno
            seqno = base
            if wnd<1:
                wnd = 1
            # print base
            # print wnd
            while seqno <= base + wnd and seqno <= size - 1:
                msg_type = 'data'
                if seqno == 0:
                    msg_type = 'start'
                elif seqno == size - 1:
                    msg_type = 'end'
                packet = self.make_packet(msg_type, seqno, msg[seqno])
                self.send(packet)
                seqno += 1
            # print type(base)

            seqno = base
            fail = False
            wr = base + wnd
            while seqno <= wr and seqno <= size - 1:
                response = self.receive(to)
                cnt = 0
                if response is None:
                    base = seqno
                    to += 0.02
                    print "t",to,wnd

                    fail = True
                    break
                    # print "t"
                else:
                    ack, flag = self.handle_response(response)
                    if not flag:
                        base = seqno
                        fail = True
                        break
                    elif ack == seqno:
                        cnt += 1
                    elif ack > seqno:
                        seqno = ack
                        cnt = 0
                        # wnd += 1
                if cnt>=3:
                    base = seqno
                    fail = True
                    break
            if not fail:
                base = seqno
                wnd += 5
                to -= 0.001
            else:
                wnd = int(wnd/2)
                msg_type = 'data'
            # print wnd
                # print base
            # print msg_type


            # print "\rsent: %s" % packet



    def handle_timeout(self):
        pass

    def handle_new_ack(self, ack):
        pass

    def handle_dup_ack(self, ack):
        pass

    def log(self, msg):
        if self.debug:
            print msg

'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:d", ["file=", "port=", "address=", "debug="])
    except:
        usage()
        exit()
    # usage()
    port = 33122
    dest = "localhost"
    filename = None
    debug = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
    # print filename
    s = Sender(dest,port,filename,debug)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
