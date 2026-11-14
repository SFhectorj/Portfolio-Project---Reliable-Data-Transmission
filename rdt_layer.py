from segment import Segment


# #################################################################################################################### #
# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #
#                                                                                                                      #
#                                                                                                                      #
# Notes:                                                                                                               #
# This file is meant to be changed.                                                                                    #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #


class RDTLayer(object):
    # ################################################################################################################ #
    # Class Scope Variables                                                                                            #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    DATA_LENGTH = 4 # in characters                     # The length of the string data that will be sent per packet...
    FLOW_CONTROL_WIN_SIZE = 15 # in characters          # Receive window size for flow-control
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    currentIteration = 0                                # Use this for segment 'timeouts'
    # Add items as needed

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0
        # Add items as needed
        self.sendBase = 0
        self.nextSeqNum = 0
        self.nextExpected = 0
        self.receiveBuffer = {}
        self.receiveData = ""

    # ################################################################################################################ #
    # setSendChannel()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable sending lower-layer channel                                                 #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # ################################################################################################################ #
    # setReceiveChannel()                                                                                              #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable receiving lower-layer channel                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # ################################################################################################################ #
    # setDataToSend()                                                                                                  #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the string data to send                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setDataToSend(self,data):
        self.dataToSend = data

    # ################################################################################################################ #
    # getDataReceived()                                                                                                #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to get the currently received and buffered string data, in order                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def getDataReceived(self):
        # ############################################################################################################ #
        # This function is called by main to get the currently received and buffered string data, in order
        # ############################################################################################################ #
        return self.receiveData

    # ################################################################################################################ #
    # processData()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # "timeslice". Called by main once per iteration                                                                   #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    # ################################################################################################################ #
    # processSend()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment sending tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processSend(self):
        windowEnd = self.sendBase + self.FLOW_CONTROL_WIN_SIZE

        # ############################################################################################################ #
        while self.nextSeqNum < len(self.dataToSend):
            payloadEnd = min(self.nextSeqNum + self.DATA_LENGTH, len(self.dataToSend))
            if payloadEnd > windowEnd:
                break  # Stop sending if the next segment would exceed the flow-control window

        # You should pipeline segments to fit the flow-control window
        # The flow-control window is the constant RDTLayer.FLOW_CONTROL_WIN_SIZE
        # The maximum data that you can send in a segment is RDTLayer.DATA_LENGTH
        # These constants are given in # characters

        # Somewhere in here you will be creating data segments to send.
        # The data is just part of the entire string that you are trying to send.
        # The seqnum is the sequence number for the segment (in character number, not bytes)


            segmentSend = Segment()                  # Segment to send data
            payload = self.dataToSend[self.nextSeqNum:payloadEnd]


        # ############################################################################################################ #
        # Display sending segment
            segmentSend.setData(str(self.nextSeqNum), payload)
            print("Sending segment: ", segmentSend.to_string())

        # Use the unreliable sendChannel to send the segment
            self.sendChannel.send(segmentSend)

            self.nextSeqNum = payloadEnd  # Update nextSeqNum to the end of the payload just sent

    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):
        receivedValidData = False 

        # ############################################################################################################ #

        for segment in self.receiveChannel.receive():
            if not segment.checkChecksum():
                print("Discarding segment with bad checksum:", segment.to_string())
                continue  # Discard segments with bad checksum
            
            if segment.seqnum == -1:
                continue  # Discard segments with invalid sequence numbers
            receivedValidData = True
            seqnum = int(segment.seqnum)

            if seqnum >= self.nextExpected:
                self.receiveBuffer[seqnum] = segment.payload

        # ############################################################################################################ #

        while self.nextExpected in self.receiveBuffer:
            payload = self.receiveBuffer.pop(self.nextExpected)
            self.receiveData += payload
            self.nextExpected += len(payload)


        # ############################################################################################################ #
        # Display response segment
        if receivedValidData:
            segmentAck = Segment()
            segmentAck.setAck(str(self.nextExpected))
            print("Sending ack: ", segmentAck.to_string())

            # Use the unreliable sendChannel to send the ack packet
            self.sendChannel.send(segmentAck)
