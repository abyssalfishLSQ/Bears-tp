#coding:UTF-8
import sys
import getopt
import socket
import random
import os
import hashlib
import time

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
#sys.argv =[sys.argv[0],'--help']
#sys.argv =[sys.argv[0],'-fREADME','-p33122','-a127.0.0.1']
#sys.argv =[sys.argv[0],'-ftest.mp4','-p33122','-a127.0.0.1']
#sys.argv =[sys.argv[0],'-ftest1.txt','-p33122','-a127.0.0.1']
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, timeout=0.5):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.debug = debug
        self.maxS_buf_size = 3 #发送方滑动窗口大小 发送窗口要小于接收窗口
        self.timeout = timeout

        self.dest = dest #这里抄StanfurdSender的
        self.dport = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',random.randint(10000,40000)))

        self.size = os.path.getsize(filename)
        self.sum_packet_num = self.size /4000  #一共要发多少包
        print "sum_packet_num %d" % self.sum_packet_num

        self.ack_seqnums = {}   #[ack , number of times received]
        self.packet_seqnums = {}  #这里为保存滑动窗口中的包，以方便重传 
        self.finished = False
        
    # Main sending loop.
    def start(self):
        msg_type = None
        base_seqno = 0
 
        while self.sum_packet_num >= 0:#滑动窗口
            #print "****************************"
            # 发
            base_seqno1 = base_seqno
            seqno = base_seqno
            #print "base_seqno= %d" % base_seqno 
            
            while seqno - base_seqno < self.maxS_buf_size and not msg_type == 'end':
                if self.size > 4000:
                    msg=self.infile.read(4000)
                else:
                    msg=self.infile.read()
                    
                msg_type = 'data' 
                if seqno == 0:
                    msg_type = 'start'   
                elif self.sum_packet_num == 0:    
                    msg_type = 'end'
                    print "end-end-end-end"
                    
                self.ack_seqnums[seqno] = 0
                #print "seqno= %d" % seqno
                packet = self.make_packet(msg_type, seqno, msg)
                self.packet_seqnums[seqno]=packet
                self.send(packet)
                seqno += 1
                self.sum_packet_num -= 1
            #发结束
            _seqno = base_seqno1
            #收
            while _seqno < base_seqno1 + self.maxS_buf_size - 1 :#模拟do-while循环
                #print "&&&&&&&&&&&&&&&&&&&&"
                response = self.receive(self.timeout)
                if response == None:#超时重传
                    print "Timeout-Timeout-Timeout"
                    for i in sorted(self.packet_seqnums.keys()):
                        self.send(self.packet_seqnums[i])


                    continue    
                else: #没超时，收到包
                    flag, need_resend_se = self.handle_response(response)#checksum是错误的包要重传 
                    if flag == False:
                        '''
                        for i in sorted(self.packet_seqnums.keys()):
                            self.send(self.packet_seqnums[i])
                        '''
                        self.send(self.packet_seqnums[need_resend_se - 1])
                        continue
                    else:# checksum没错误
                        msg1_type, _seqno, data, checksum = self.split_packet(response)
                        _seqno = int(_seqno) - 1
                        #print "_seqno= %d" % _seqno #测试测试测试
                        self.ack_seqnums[_seqno] += 1
                        
                        if self.ack_seqnums[_seqno] >= 3:   #收到3次ack重传
                            print "dumplicate-ACK-dumplicate-ACK-dumplicate-ACK"
                            for i in sorted(self.packet_seqnums.keys()):
                                self.ack_seqnums[i] = 0 #ack次数重新记为0
                                self.send(self.packet_seqnums[i])
                                break
                            #continue
                        else: #收到正确的包
                            if _seqno == base_seqno:#发送窗口往前移一格
                                del self.packet_seqnums[base_seqno]
                                del self.ack_seqnums[base_seqno]
                                base_seqno += 1
                                #print "base_seqno= %d" % base_seqno   #测试测试
                                
                if msg_type == 'end':
                    print "BBBBBBBBBBBBBB"
                    self.sum_packet_num -= 1 #因为是模拟do-while循环，为防止死循环，当它是最后一个包时直接跳出循环
                    break
            
                    
        self.infile.close()
        print "-infile-Close-infile-Close-infile-Close-"

    def handle_response(self,response_packet):
        msg_type, seqno, data, checksum = self.split_packet(response_packet)
        if Checksum.validate_checksum(response_packet):
            print "recv: %s" % response_packet
            return eval(seqno), True 
        else:
            #print "recv: %s <--- CHECKSUM FAILED" % response_packet
            return eval(seqno), False

            
    def handle_timeout(self):
        pass

    def handle_new_ack(self, ack):
        pass

    def handle_dup_ack(self, ack):#超3次出现同样的ack重发
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

    s = Sender(dest,port,filename,debug)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
