import sys
import struct


class FAT32:
    END_CLUSTER = 0x0fffffff
    dir_list=[]
    file_list=[]

    def __init__(self, filename):
        self.filename = filename
        self.fd = open(filename, "rb")
        self.read_vbr()

    def read_vbr(self): # vbr 1섹터 읽기
        self.fd.seek(0)
        vbr = self.fd.read(512)
        self.bps = struct.unpack_from("<H", vbr, 11)[0]
        self.spc = struct.unpack_from("<B", vbr, 13)[0]
        self.reserved_sectors = struct.unpack_from("<H", vbr, 14)[0]
        self.number_of_fats = struct.unpack_from("<B", vbr, 16)[0]
        self.sectors = struct.unpack_from("<I", vbr, 32)[0]
        self.fat_size = struct.unpack_from("<I", vbr, 36)[0]
        self.root_cluster = struct.unpack_from("<I", vbr, 44)[0]
        self.first_data_sector = self.fat_size * self.number_of_fats + self.reserved_sectors


    def read_sector(self, offset, count=1):
        self.fd.seek(offset * self.bps)
        return self.fd.read(self.bps * count)

    def read_cluster(self, cluster, count=1):
        if cluster < 2:
            raise Exception("Can't read under cluster 2")

        real_cluster = cluster - 2
        return self.read_sector(self.first_data_sector + real_cluster * self.spc, count * self.spc)

    def seek(self, offset, whence=0):
        self.fd.seek(offset, whence)

    def read_clusters(self, fats):
        data = bytes(0)
        for i in fats:
            data += self.read_cluster(i)

        return data

    def to_decode(self, data, encoding):
        if len(data) == 0:
            return ""

        return data.decode(encoding)

    def to_utf_16_le(self, data):
        return self.to_decode(data, 'utf-16-le')

    def to_euc_kr(self, data):
        return self.to_decode(data, 'euc-kr')

    def filter_unused_lfn(self, data):
        length = len(data)
        for i in range(len(data), 0, -2):
            if data[i - 2:i] == b'\xff\xff' or data[i - 2:i] == b'\x00\x00':
                length = i - 2
            else:
                break

        return data[:length]

    def parse_dir_entry_lfn(self, data, lfn):
        order = data[0]
        name1 = self.to_utf_16_le(self.filter_unused_lfn(data[1:11]))
        name2 = self.to_utf_16_le(self.filter_unused_lfn(data[14:26]))
        name3 = self.to_utf_16_le(self.filter_unused_lfn(data[28:32]))

        return {'name': name1 + name2 + name3 + lfn}

    def parse_dir_entry(self, data, lfn):
        attr = data[11]
        is_LFN = attr & 0x0F is 0x0F

        if data[0]==0xE5 :
            name='!'
            name=name+self.to_euc_kr(data[2:7]).rstrip()
        else :
            name = self.to_euc_kr(data[0:8]).rstrip()

        ext = self.to_euc_kr(data[8:11]).rstrip()

        if len(ext) > 0:
            name = name + "." + ext

        highcluster = struct.unpack_from("<H", data, 20)[0]
        lowcluster = struct.unpack_from("<H", data, 26)[0]
        cluster = highcluster << 16 | lowcluster
        size = struct.unpack_from("<I", data, 28)[0]
        entry = {'sname': name, 'attr': attr, 'cluster': cluster, 'size': size}
        if len(lfn) > 0:
            entry['name'] = lfn

        if data[0] == 0xE5:
            entry['del']='deleted'

        return entry

    def get_content(self, cluster):
        fats = self.get_fats_by_start_cluster(cluster)
        return self.read_clusters(fats)

    def get_files(self, cluster):
        fats = self.get_fats_by_start_cluster(cluster)
        data = self.read_clusters(fats)

        lfn = ""
        for i in range(0, len(data), 32):
            entry_data = data[i:i + 32]  # 한 entry 씩 땡기네
            c = struct.unpack("<QQQQ", entry_data)
            if c[0] == 0 and c[1] == 0 and c[2] == 0 and c[3] == 0:
                break

            attr = entry_data[11]
            is_LFN = attr & 0x0F is 0x0F

            if not is_LFN:
                entry = self.parse_dir_entry(entry_data, lfn.strip())
                lfn = ""
                #print(entry)
                self.define_dir(entry)
            else:
                entry = self.parse_dir_entry_lfn(entry_data, lfn)
                lfn = entry['name']

    def get_fats_by_start_cluster(self, cluster, fat=1):
        # To get fat chain, it uses fat.
        base_sector = self.reserved_sectors + self.fat_size * (fat - 1)
        fats_per_sector = self.bps / 4

        fats = []

        next_cluster = cluster
        while next_cluster != self.END_CLUSTER:
            fats.append(next_cluster)
            sector, idx = divmod(next_cluster, fats_per_sector)
            sector = int(sector)
            idx = int(idx)

            data = self.read_sector(base_sector + sector)
            next_cluster = struct.unpack_from("<I", data, idx * 4)[0]

        return fats

    def define_dir(self,entry):

       if entry['attr']==8 :
           print("volume :" + entry['sname'] + '    ' + str(entry['attr']))

       if entry['attr']==16 or entry['attr']==22 :
           # print("dir :" + entry['sname'] + '    ' + str(entry['attr']))
            self.dir_list.append(entry)

       else:
            #print("file :" + entry['sname']+ '   '+str(entry['attr']))
            self.file_list.append(entry)


    def generateView(self, text):
        space = ' '

        rowSpacing = 4
        rowLength = 16
        byteWidth=4

        offset = 0

        offsetText = ''
        mainText = ''
        asciiText = ''

        for chars in range(1, len(text) + 1):
            byte = text[chars - 1]
            char = chr(text[chars - 1])

            # Asciitext 는 오른쪽 출력부
            if char is ' ':
                asciiText += '.'

            elif char is '\n':
                asciiText += '!'

            else:
                asciiText += char
            # main text 가 중앙에 있는것
            mainText += format(byte, '0' + str(byteWidth) + 'x')

            if chars % rowLength is 0:
                offsetText += format(offset, '08x') + '\n'
                mainText += '\n'
                asciiText += '\n'

            elif chars % rowSpacing is 0:
                mainText += space * 2

            else:
                mainText += space

            offset += len(char)
        print(mainText)

    def renew_list(self):
        self.dir_list=[]
        self.file_list=[]


if __name__ == '__main__':
    print("Fat32")

    fs = FAT32(sys.argv[1])
    #data = fs.read_cluster(fs.root_cluster) #root cluster 의 값을 read
    #fs.print_all_disk();

    fs.get_files(fs.root_cluster)
    print(fs.dir_list)

    #for i in fs.dir_list:
    #    print(i['sname'])

    #print(fs.get_files(FAT32.dir_list[5]['cluster']))
    fs.renew_list()
    fs.get_files(7)
    for i in fs.dir_list:
        print(i['sname'])

   # for i in FAT32.dir_list:
    #    if 'del' in i:
    #        print(i)