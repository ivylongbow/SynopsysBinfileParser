import sys
from PyQt5.QtWidgets import *
import os


class FileDialogOpen(QWidget):
    def __init__(self, parent=None):
        super(FileDialogOpen, self).__init__(parent)
        layout = QVBoxLayout()
        self.btn = QPushButton("Load Bin File")
        self.btn.clicked.connect(self.load_file)
        layout.addWidget(self.btn)
        self.setLayout(layout)
        self.setWindowTitle("File Dialog demo")

    def load_file(self):
        filter_extension = 'BIN (*.bin)'
        file_path = QFileDialog.getOpenFileName(caption='Open BIN File', filter=filter_extension)
        # Open bin file
        if len(file_path[0]) == 0:
            pass
        else:
            if len(file_path[0]) > 1:
                filename = file_path[0]
                filename_si = os.path.splitext(filename)[0]+'_si.txt'
                filename_so = os.path.splitext(filename)[0]+'_so.txt'
                filename_rm = os.path.splitext(filename)[0]+'_readme.txt'
                with open(filename, 'rb') as binfile:
                    # print(filename)
                    # packetsize = int.from_bytes(binfile.read(4), byteorder='little', signed=False)
                    bf = BinFileSynopsys(binfile)
                    # readme text file
                    bf.print_header(filename_rm)
                    # generate scan in data
                    bf.generate_stimulus(filename_si)
                    # generate scan out data
                    bf.generate_expected_and_mask(filename_so)

            else:
                print('No file selected')


class DataPackets:
    def __init__(self, data, length: int):
        self.data = data
        self.length = int(length)


class BinFileSynopsys:
    def __init__(self, fname):
        self.fname = fname
        self.location = 1

        # 0	    uint32_t	Packet size in bits (this is 32 today)
        self.lastread = fname.read(4)
        self.packetsize = int.from_bytes(self.lastread, byteorder='little', signed=False)   # in bits
        # 1	    uint32_t	Header size (in packets, i.e 4-byte words)
        self.lastread = fname.read(4)
        packet_length = int.from_bytes(self.lastread, byteorder='little', signed=False)
        # 1.1   char		Header ASCII text, padded with '\0' only if necessary to meet a packet boundary.
        self.lastread = fname.read(int(self.packetsize / 8 * packet_length))
        self.ascii_header = DataPackets(self.lastread, packet_length)
        # 2     uint32_t	Stimulus data size (in packets)
        self.lastread = fname.read(4)
        packet_length = int.from_bytes(self.lastread, byteorder='little', signed=False)
        # 2.1   binary 		Stimulus data block
        self.lastread = fname.read(int(self.packetsize / 8 * packet_length))
        self.stimulus = DataPackets(list(self.lastread), packet_length)
        # 3     uint32_t	Expected plus mask total total size (in packets)
        self.lastread = fname.read(4)
        packet_length = int.from_bytes(self.lastread, byteorder='little', signed=False)
        # 3.1   binary		Expected data block (number of packets/2)
        self.lastread = fname.read(int(self.packetsize / 8 * packet_length / 2))
        self.expected = DataPackets(list(self.lastread), packet_length // 2)
        # 3.2   binary		Mask data block (number of packets/2)
        self.lastread = fname.read(int(self.packetsize / 8 * packet_length / 2))
        self.mask = DataPackets(list(self.lastread), packet_length // 2)

    def print_header(self, filename, debug_print=False):
        with open(filename, 'wb') as rm_file:
            rm_file.write(self.ascii_header.data)
            if debug_print:
                print(self.ascii_header.data)

    def generate_stimulus(self, filename, debug_print=False):
        with open(filename, 'w') as si_file:
            for element in self.stimulus.data:
                si_file.writelines(str(element) + '\n')
            if debug_print:
                print('stimulus packets: ', self.stimulus.length)

    def generate_expected_and_mask(self, filename, debug_print=False):
        with open(filename, 'w') as so_file:
            for element in self.expected.data:
                so_file.writelines(str(element) + '\n')
            if debug_print:
                print('expected packets: ', self.expected.length)
            for element in self.mask.data:
                so_file.writelines(str(element) + '\n')
            if debug_print:
                print('mask packets: ', self.mask.length)
    #
    # def seek(self, location):
    #     self.location = location
    #     self.fname.seek(self.location)
    #
    # def get_packets(self, readlength=0):
    #     if readlength:
    #         self.lastread = self.fname.read(int(4 * self.packetsize / 8 * readlength))
    #         return self.lastread
    #     else:
    #         self.lastread = self.fname.read(4)
    #         packet_length = int.from_bytes(self.lastread, byteorder='little', signed=False)
    #         self.lastread = self.fname.read(int(self.packetsize / 8 * packet_length))
    #         return self.lastread


def main():
    app = QApplication(sys.argv)
    ex = FileDialogOpen()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()