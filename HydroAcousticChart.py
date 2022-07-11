import struct
import time

import numpy as np
import pandas as pd


class HydroAcousticChart:
    def __init__(self, file):
        self.file = file

    def decode_hat(self):

        with open(self.file, mode='rb') as file:
            data = file.read()

        hat = ['Time start', 'Time stop', 'Message type_a11', 'Message len_a11', 'Sender_a11', 'Receiver_a11',
               'Reserv_a11',
               'Reserv_a112', 'Reserv_a113', 'Reserv_a114', 'Unique ID_a11', 'Start_a11', 'Ant Code', 'Frequency diap',
               'Message type_a12', 'Message len_a12', 'Sender_a12', 'Receiver_a12', 'Reserv_a121', 'Reserv_a122',
               'Reserv_a123',
               'Reserv_a124', 'Unique ID_a12', 'Range, m', 'DN width hor', 'DN width vert', 'DN angle hor',
               'DN angle vert',
               'Impuls len', 'Impuls type', 'Gain', 'VARU', 'Izl mode', 'PM mode', 'Freq Diap Code(PICT)',
               'Message type_a31',
               'Message len_a31', 'Sender_a31', 'Receiver_a31', 'Reserv_a311', 'Reserv_a312', 'Reserv_a313',
               'Reserv_a314',
               'Unique ID_a31', 'Start_a31', 'Range_a31', 'Reserv1', 'Message type_a32', 'Message len_a32',
               'Sender_a32',
               'Receiver_a32', 'Reserv_a321', 'Reserv_a322', 'Reserv_a323', 'Reserv_a324', 'Unique ID_a32', 'Start_a32',
               'Range_a32', 'Reserv_a32']
        val = struct.unpack('=dd8HIH2B8HIH2B2cH6B8HI3H8HI3H', data[:126])
        result = list(zip(hat, val))
        res = pd.DataFrame(result).set_index(0).T
        res.iloc[0, 0] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result[0][1]))
        case = res['Receiver_a11'][1]
        # Для антенны КГАСМ
        mode = False
        if res['Start_a11'][1] == 0 and res['Start_a31'][1] > 0:
            mode = True
        # 384 канала, порядок уже есть KGASM_PO_LF
        if case == 4369:
            if mode:
                prnt = 'GANS_PO'
                return 'BOP_GANS_PR', prnt, 96
            else:
                prnt = 'KGASM_PO_LF'
                return 'KGASM_PO_LF_PR', prnt, 384

        elif case == 4385:
            if mode:
                prnt = 'GANS_BOL'
                return 'BOP_GANS_PR', prnt, 96
            else:
                prnt = 'KGASM_BOL_LF'
                return 'KGASM_PO_LF_PR', prnt, 384

        elif case == 4401:
            if mode:
                prnt = 'GANS_BOP'
                return 'BOP_GANS_PR', prnt, 96
            else:
                prnt = 'KGASM_BOP_LF'
                return 'KGASM_PO_LF_PR', prnt, 384
        # 384 канала, порядок уже есть KGASM_PO_LF

        # В этом случае 352 канала, очередность переопределяется файлом KGASM/BOL_HF_PR
        elif case == 4370:
            prnt = 'KGASM_PO_HF'
            return 'KGASM_BOL_HF_PR', prnt, 352

        elif case == 4386:
            prnt = 'KGASM_BOL_HF'
            return 'KGASM_BOL_HF_PR', prnt, 352

        elif case == 4402:
            prnt = 'KGASM_BOP_HF'
            return 'KGASM_BOL_HF_PR', prnt, 352

        elif case == 4419:
            prnt = 'ZO_GANS'
            return 'ZO_GANS_PR', prnt, 96
        # В этом случае 352 канала, очередность переопределяется файлом KGASM/BOL_HF_PR
        # Для антенны СПА
        # 384 канала, очередность устанавливается файлом PO_LF_PR
        elif case == 8721:
            prnt = 'SPA_PO_LF'
            return 'SPA_PO_LF_PR', prnt, 384
        # 216 каналов, очередность устанавливается файлов PO_HF_PR
        elif case == 8722:
            prnt = 'SPA_PO_HF'
            return 'SPA_PO_HF_PR', prnt, 216
        # 140 каналов, очередность устанавливается файлом BOL_HF_PR
        elif case == 8738:
            prnt = 'SPA_BOL_HF'
            return 'SPA_BOL_HF_PR', prnt, 140
        elif case == 8754:
            prnt = 'SPA_BOP_HF'
            return 'SPA_BOL_HF_PR', prnt, 140
        # для антенн БТ
        # 60 каналов, очередность устанавливается файлом NO_LF_PR
        elif case == 9025:
            prnt = 'BT_NO_LF'
            return 'BT_NO_LF_PR', prnt, 60
        # 200 каналов, очередность устанавливается файлом NO_HF_PR
        elif case == 9026:
            prnt = 'BT_NO_HF'
            return 'BT_NO_HF_PR', prnt, 200
        # 120 каналов, очередности устанавливаются файлами BOL_LF_PR и BOP_LF_PR
        elif case == 8993:
            prnt = 'BT_BOL_LF'
            return 'BT_BOL_LF_PR', prnt, 120
        elif case == 9009:
            prnt = 'BT_BOP_LF'
            return 'BT_BOP_LF_PR', prnt, 120

    def remap(self):
        name, prnt, ch_num = self.decode_hat()
        with open(fr'Profiles/{name}.ini') as data:
            mapnew = []
            for line in data:
                mapnew.append(int(line.strip().split('\t')[1]))
        return mapnew

    def decode_bin(self):
        with open(self.file, mode='rb') as file:
            data = file.read()
        bin_len = int((len(data) - 1150) / 2)
        data_ints = struct.unpack('h' * bin_len, data[1150:])
        remap, name, ch_num = self.decode_hat()
        res = pd.DataFrame(np.reshape(np.array(data_ints), (len(data_ints) // ch_num, ch_num)),
                           columns=[i for i in range(1, ch_num + 1)]) ** 2
        res = res.groupby(res.index // 2).sum() ** 0.5
        res.index += 1
        remap = self.remap()
        for i in range(len(remap)):
            remap[i] -= 1
        res = res[res.columns[remap]]
        res.columns = [i for i in range(1, len(res.columns) + 1)]
        return res

    def re_im_values(self):
        with open(self.file, mode='rb') as file:
            data = file.read()
        bin_len = int((len(data) - 1150) / 2)
        data_ints = struct.unpack('h' * bin_len, data[1150:])
        remap, name, ch_num = self.decode_hat()
        c = pd.DataFrame(np.reshape(np.array(data_ints), (len(data_ints) // ch_num, ch_num)),
                         columns=[i for i in range(1, ch_num + 1)])
        c1 = c.iloc[1::2, :]
        c2 = c.iloc[0::2, :]
        c1.index = [i for i in range(1, len(c1) + 1)]
        c2.index = [i for i in range(1, len(c1) + 1)]
        c3 = c2 + c1 * 1j
        return c3

    def build_graph(self, ch_st=0, ch_en=385):

        res = self.decode_bin()
        pd.options.plotting.backend = "plotly"
        return res.iloc[:, ch_st:ch_en].plot.line(
            labels={'value': 'Значение', 'index': 'Номер измерения', 'variable': 'Канал'},
            title='График абсолютных значений в каналах')

    def info(self):
        remap, name, ch_num = self.decode_hat()
        return name, ch_num