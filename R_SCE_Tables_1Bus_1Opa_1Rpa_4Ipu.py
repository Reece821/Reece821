import sys
import struct
import time
import msfe

######################################################################
def run(scpa, fd):
    def Transmit (scpa, fd, mess):
        scpa.send(mess)
        fd.write(str(mess))
        fd.write('Sent request nr %s (exch id=%s)\n' % (send_count, mess.hdr.exch_id))
        time.sleep(1.0)

    def TxWaitRx(msg):
        scpa.send(msg)
        fd.write(str(msg) + '\n')
        resp = scpa.poll(req=msg)
        fd.write('Got response = %s\n' % resp)
        return resp
    #
    # Clear out any response messages that might be left over from other scripts
    while 1:
        resp = scpa.poll(timeout=1.0)
        if not resp:
            break
    #
    send_count = 0

    mess = msfe.sce.SceRequest()
    mess.hdr.function = 16 # Download Table

    # Table config
    # Constant Values
    FireAngle = 30
    CollisionAvoidance = 0
    SyncState = 6
    DtC = 12 #Detection Window Count
    DtD = 5  #Detection Window Degrees
    DtB = 7  #Detection Window Bits
    OpStat = 1 #Operational Status of Equipment

    #
    # OMU Map
    #         Bus OmuId
    OMUmap = [
              (1,  1)#,
              #(1,  2)
			  ]
    #
    # IPU Map
    #         Bus Fdr DetPt IPU   
    IPUmap = [
              (1,  1,  'A',  0),
              (1,  1,  'B',  1),
              (1,  1,  'C',  2),
              (1,  1,  'N',  3)
    ]
    #
    # OMU Parameters
    #          OmuId
    OMUparm = [
               (1, FireAngle, FireAngle, FireAngle, FireAngle, FireAngle, FireAngle, CollisionAvoidance)#,
               #(2, FireAngle, FireAngle, FireAngle, FireAngle, FireAngle, FireAngle, CollisionAvoidance)
    ]
    #
    # Receiver Parameters
    #          RpaId
    RPAparm = [
               (1, SyncState)
    ]
    #
    # Detection parameters:
    #           Bus Fdr MultBit DetCor   ChSet ChMap  GChSet GChMap LGPhD LLPhD DetWC DetWD DetWB NScal PhScal AdFilt BitOp1 BitOp2
    # Min       1   1   0       crc       A    000001  A     000001  5    5     12    5     7     1     1      0      0x00   0x00
    # Max       254 254 1       crc_hamm  F    111111  F     111111  175  175                     100   100    255    0xFF   0xFF
    DetParm = [
               (1,  1,  0,   'crc_hamm', 'A', '000001','A', '111111',130, 130,  DtC,  DtD,  DtB,  100,  100,   0,     0x20,  0x00)
    ]
    #
    # Equipment Table
    #        EqType EqId OpStat PhMap HwV HwV2 SwV SwV2
    #        1 OMU  1-12    1      0   0    0    0   0
    #        2 RPA  1-4
    #        3 SCPA 0
    #        7 IPU  0-127
    EqTab = [
             (1,     1,    OpStat, 0, 0, 0, 0, 0),
             #(1,     2,    OpStat, 0, 0, 0, 0, 0),
             (2,     1,    OpStat, 0, 0, 0, 0, 0),
             (3,     0,    OpStat, 0, 0, 0, 0, 0),
             (7,     0,    OpStat, 0, 0, 0, 0, 0),
             (7,     1,    OpStat, 0, 0, 0, 0, 0),
             (7,     2,    OpStat, 0, 0, 0, 0, 0),
             (7,     3,    OpStat, 0, 0, 0, 0, 0)
    ]
    #
    #
    tables = [msfe.tables.OMU_Map(OMUmap),
              msfe.tables.IPU_Map(IPUmap),
              msfe.tables.OMU_Params(OMUparm),
              msfe.tables.Rcvr_Params(RPAparm),
              msfe.tables.Det_Params(DetParm),
              msfe.tables.Eq_Table(EqTab)
    ]

    # Lock the Tables
    mess = msfe.sce.LockTablesRequest(tables)
    Transmit(scpa, fd, mess)
    send_count += 1

    resp = scpa.poll(req=mess, timeout=60.0)

    if resp:
        fd.write('Got response = %s\n' % resp)
        if resp.hdr.executionStatus != 0:
            fd.write('ERROR - BAD EXECUTION STATUS %s\n' % resp.hdr.executionStatus)
        else:
            # Download the Tables
            for table in tables:
                mess = msfe.sce.DownloadTableRequest(table)
                Transmit(scpa, fd, mess)
                send_count += 1

                resp = scpa.poll(req=mess, timeout=60.0)

                if resp:
                    fd.write('Got response = %s\n' % resp)
                    if resp.hdr.executionStatus != 0:
                        fd.write('ERROR - BAD EXECUTION STATUS %s\n' % resp.hdr.executionStatus)
                else:
                    fd.write('ERROR - No Response Received')
    else:
        fd.write('ERROR - No Response Received')



    # Unlock the Tables
    mess = msfe.sce.UnlockTablesRequest(tables)
    Transmit(scpa, fd, mess)
    send_count += 1

    resp = scpa.poll(req=mess, timeout=60.0)

    if resp:
        fd.write('Got response = %s\n' % resp)
        if resp.hdr.executionStatus != 0:
            fd.write('ERROR - BAD EXECUTION STATUS %s\n' % resp.hdr.executionStatus)
    else:
        fd.write('ERROR - No Response Received')


    # Done
    return
    

